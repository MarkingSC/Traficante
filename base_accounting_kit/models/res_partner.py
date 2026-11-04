# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# Facturas que se consideran cartera vigente: publicadas, con saldo pendiente.
FOLLOWUP_INVOICE_DOMAIN = [('state', '=', 'posted'),
                           ('invoice_payment_state', '=', 'not_paid'),
                           ('type', '=', 'out_invoice'),
                           ('amount_residual', '>', 0)]

FOLLOWUP_STATUS = [('in_need_of_action', 'In need of action'),
                   ('with_overdue_invoices', 'With overdue invoices'),
                   ('no_action_needed', 'No action needed')]


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_list = fields.One2many('account.move', 'partner_id',
                                   string="Invoice Details",
                                   readonly=True,
                                   domain=list(FOLLOWUP_INVOICE_DOMAIN))

    # Seguimiento por sucursal: las facturas se agrupan por dirección de
    # entrega (account.move.followup_partner_id) en lugar de por cliente.
    branch_invoice_list = fields.One2many('account.move', 'followup_partner_id',
                                          string="Invoice Details",
                                          readonly=True,
                                          domain=list(FOLLOWUP_INVOICE_DOMAIN))
    branch_total_due = fields.Monetary(string="Total Due",
                                       compute='_compute_for_branch_followup',
                                       readonly=True)
    branch_total_overdue = fields.Monetary(
        string="Total Overdue", compute='_compute_for_branch_followup',
        readonly=True)
    branch_next_reminder_date = fields.Date(
        string="Next Reminder Date", compute='_compute_for_branch_followup',
        readonly=True)
    branch_followup_status = fields.Selection(
        FOLLOWUP_STATUS, string='Followup status',
        compute='_compute_for_branch_followup',
        search='_search_branch_followup_status', readonly=True)

    total_due = fields.Monetary(compute='_compute_for_followup', store=False,
                                readonly=True)
    next_reminder_date = fields.Date(compute='_compute_for_followup',
                                     store=False, readonly=True)
    total_overdue = fields.Monetary(compute='_compute_for_followup',
                                    store=False, readonly=True)
    followup_status = fields.Selection(
        [('in_need_of_action', 'In need of action'),
         ('with_overdue_invoices', 'With overdue invoices'),
         ('no_action_needed', 'No action needed')],
        string='Followup status',
        )

    def _compute_for_followup(self):
        """
        Compute the fields 'total_due', 'total_overdue' , 'next_reminder_date' and 'followup_status'
        """
        for record in self:
            total_due = 0
            total_overdue = 0
            today = fields.Date.today()
            for am in record.invoice_list:
                if am.company_id == self.env.company:
                    amount = am.amount_residual
                    total_due += amount
                    is_overdue = today > am.invoice_date_due if am.invoice_date_due else today > am.date
                    if is_overdue:
                        total_overdue += not am.invoice_sent and amount or 0
            min_date = record.get_min_date()
            action = record.action_after() or 0
            if min_date:
                date_reminder = min_date + timedelta(days=action)
                if date_reminder:
                    record.next_reminder_date = date_reminder
            else:
                date_reminder = today
                record.next_reminder_date = date_reminder
            if total_overdue > 0 and date_reminder > today:
                followup_status = "with_overdue_invoices"
            elif total_due > 0 and date_reminder <= today:
                followup_status = "in_need_of_action"
            else:
                followup_status = "no_action_needed"
            record.total_due = total_due
            record.total_overdue = total_overdue
            record.followup_status = followup_status

    def get_min_date(self):
        today = date.today()
        for this in self:
            if this.invoice_list:
                min_list = [d for d in this.invoice_list.mapped('invoice_date_due') if d]
                return min(min_list) if min_list else today
            else:
                return today

    def get_delay(self):
        delay = """select id,delay from followup_line where followup_id =
        (select id from account_followup where company_id = %s)
         order by delay limit 1"""
        self._cr.execute(delay, [self.env.company.id])
        record = self.env.cr.dictfetchall()
        return record

    def action_after(self):
        lines = self.env['followup.line'].search([(
            'followup_id.company_id', '=', self.env.company.id)])
        if lines:
            record = self.get_delay()
            for i in record:
                return i['delay']

    # ------------------------------------------------------------------
    # Seguimiento por sucursal
    # ------------------------------------------------------------------
    @api.model
    def _get_followup_values(self, invoices, today, delay):
        """Calcula los totales y el estado de seguimiento de un conjunto de
        facturas con la misma lógica que _compute_for_followup."""
        total_due = 0.0
        total_overdue = 0.0
        for am in invoices:
            if am.company_id == self.env.company:
                amount = am.amount_residual
                total_due += amount
                is_overdue = today > am.invoice_date_due if am.invoice_date_due else today > am.date
                if is_overdue:
                    total_overdue += not am.invoice_sent and amount or 0
        due_dates = [d for d in invoices.mapped('invoice_date_due') if d]
        min_date = min(due_dates) if due_dates else today
        date_reminder = min_date + timedelta(days=delay)
        if total_overdue > 0 and date_reminder > today:
            status = "with_overdue_invoices"
        elif total_due > 0 and date_reminder <= today:
            status = "in_need_of_action"
        else:
            status = "no_action_needed"
        return {
            'total_due': total_due,
            'total_overdue': total_overdue,
            'next_reminder_date': date_reminder,
            'status': status,
        }

    def _compute_for_branch_followup(self):
        """
        Compute 'branch_total_due', 'branch_total_overdue',
        'branch_next_reminder_date' and 'branch_followup_status'
        """
        today = fields.Date.today()
        delay = self.action_after() or 0
        for record in self:
            values = self._get_followup_values(record.branch_invoice_list, today, delay)
            record.branch_total_due = values['total_due']
            record.branch_total_overdue = values['total_overdue']
            record.branch_next_reminder_date = values['next_reminder_date']
            record.branch_followup_status = values['status']

    @api.model
    def _search_branch_followup_status(self, operator, value):
        """El estado de sucursal no se guarda: se evalúa sobre las facturas
        pendientes actuales, agrupadas por sucursal."""
        if operator not in ('=', '!=', 'in', 'not in'):
            raise UserError(_('Operation not supported'))
        wanted = set(value) if isinstance(value, (list, tuple, set)) else {value}
        positive = operator in ('=', 'in')

        today = fields.Date.today()
        delay = self.action_after() or 0
        Move = self.env['account.move']
        invoices = Move.search(FOLLOWUP_INVOICE_DOMAIN + [('followup_partner_id', '!=', False)])
        invoice_ids_by_branch = {}
        for invoice in invoices:
            invoice_ids_by_branch.setdefault(invoice.followup_partner_id.id, []).append(invoice.id)

        # Las sucursales sin facturas pendientes siempre son 'no_action_needed'.
        status_by_branch = {
            branch_id: self._get_followup_values(Move.browse(ids), today, delay)['status']
            for branch_id, ids in invoice_ids_by_branch.items()}
        matching = [b for b, st in status_by_branch.items() if st in wanted]
        not_matching = [b for b, st in status_by_branch.items() if st not in wanted]

        if 'no_action_needed' in wanted:
            if positive:
                return [('id', 'not in', not_matching)]
            return [('id', 'in', not_matching)]
        if positive:
            return [('id', 'in', matching)]
        return [('id', 'not in', matching)]
