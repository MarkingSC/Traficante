# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from email.policy import default
from odoo import fields, models, api
from datetime import timedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sh_no_mail = fields.Boolean("Don't Send Unpaid Email Notification", default=True)


class AccountMove(models.Model):
    _inherit = 'account.move'

    sh_remainder_history_ids = fields.One2many(
        'sh.remainder.history', 'invoice_id', string='Reminder History')

    @api.model
    def unpaid_invoice_notify_fun(self):
        if self.env.user.company_id.unpaid_reminder:
            for remainder in self.env['sh.unpaid.remainder.config'].sudo().search([]):
                today = fields.Date.today()
                remainder_days = 0
                remainder_date = None
                if remainder.sh_remainder_days < 0:
                    remainder_days = remainder_days - remainder.sh_remainder_days
                    remainder_date = today + timedelta(remainder_days)
                else:
                    remainder_days = remainder.sh_remainder_days
                    remainder_date = today - timedelta(remainder_days)

                if self.env.user.company_id.notify_on == 'due_date':

                    date_invoice_search = self.env['account.move'].search(
                        [('type', '=', 'out_invoice'), ('state', '=', 'posted'), ('amount_residual_signed', '>', '0'), ('invoice_date_due', '<=', remainder_date)])

                elif self.env.user.company_id.notify_on == 'inv_date':
                    date_invoice_search = self.env['account.move'].search(
                        [('type', '=', 'out_invoice'), ('state', '=', 'posted'), ('amount_residual_signed', '>', '0'), ('invoice_date', '<=', remainder_date)])

                if date_invoice_search:
                    for record in date_invoice_search:

                        if record.partner_id and (record.partner_id.email and not record.partner_id.sh_no_mail):
                            if remainder.sh_template_id:
                                template = remainder.sh_template_id
                            else:
                                template = self.env.ref(
                                    'sh_unpaid_invoice_reminder.template_account_unpaid_invoice_reminder_email')
                            if template:
                                mail_res = template.send_mail(
                                    record.id, force_send=True, notif_layout='mail.mail_notification_paynow')
                                self.env['sh.remainder.history'].sudo().create({
                                    'invoice_id': record.id,
                                    'sh_mail_date': fields.Date.today(),
                                    'sh_mail_id': mail_res,
                                })


class RemainderHistory(models.Model):
    _name = 'sh.remainder.history'
    _description = 'Remainder History'

    sh_mail_date = fields.Date(string='Mail Date')
    sh_mail_id = fields.Many2one('mail.mail', string='Mail')
    invoice_id = fields.Many2one('account.move', string='Invoice')
