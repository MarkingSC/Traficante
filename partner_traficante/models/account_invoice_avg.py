
import logging
from datetime import  datetime, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
import pytz


_logger = logging.getLogger(__name__)
class AccountInvoiceAvg(models.Model):

    _name= "account.invoice.avg"

    partner_id = fields.Many2one('res.partner', string = "Partner", ondelete = "cascade")
    date = fields.Date(string = 'Date')
    average = fields.Float(string = "Average")
    amount = fields.Float(string = "Amount")

    @api.model
    def _get_tz_datetime(self, in_datetime):
        tz = pytz.timezone(str(self.env.user.tz))
        now_user = tz.fromutc(in_datetime).replace(tzinfo=None)
        return now_user

    @api.model
    def _get_last_day_date(self, last_date):
        dt = last_date.replace(day=1) + relativedelta(months=1) - relativedelta(days=1)
        return date(dt.year, dt.month, dt.day)

    @api.model
    def _update_amount(self, last_date, partner):
        last_day_date = self._get_last_day_date(last_date)
        # Looks for an avg record for the given values
        avg_record = self.search([
            ('date', '=', last_day_date),
            ('partner_id', '=', partner.id)], limit=1)

        # If didn't find a record creates a new one
        if not avg_record:
            avg_record = self.create(
                {
                    'partner_id': partner.id,
                    'date': last_day_date,
                })

        # Looks for regular invoices for that month and year
        invoices = self.env['account.move'].search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'posted'),
            ('type', '=', 'out_invoice'),
            ('invoice_date', '<=', last_day_date),
            ('invoice_date', '>=', last_day_date.replace(day=1))])

        # Looks for refund invoices from invoices for that month and year
        invoice_ids = invoices.mapped('id')
        refund_invoices = self.env['account.move'].search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'posted'),
            ('type', '=', 'out_refund'),
            ('reversed_entry_id', 'in', invoice_ids)])

        # Gets only invoices amount
        invoices_amount = invoices.mapped('amount_total')
        refund_invoices_amount = refund_invoices.mapped('amount_total')

        # Sum invoices amount to get total amount
        amount_sum = sum(invoices_amount)
        refund_amount_sum = sum(refund_invoices_amount)
        real_amount = amount_sum - refund_amount_sum

        # Writes invoices total amount on avg record
        avg_record.write(
            {
                'amount': real_amount
            })

        return avg_record


    @api.model
    def _update_avg(self, last_date, partner):
        last_day_date = self._get_last_day_date(last_date)
        months_between = (last_day_date.year - partner.create_date.year) * 12 + \
                         (last_day_date.month - partner.create_date.month) + 1
        if months_between > 12:
            months_between = 12
            first_date = self._get_last_day_date(last_day_date - relativedelta(months=12) + relativedelta(days=1))
        else:
            first_date = partner.create_date.date()

        avg_records = self.search([('date', '>=', first_date),
                                   ('date', '<=', last_day_date)])

        avg_amounts = avg_records.mapped('amount')

        avg_amount_sum = sum(avg_amounts)

        avg_amount_avg = avg_amount_sum / months_between

        current_avg = self.search([('date', '=', last_day_date)], limit=1)

        if not current_avg:
            current_avg = self._update_amount(last_day_date, partner)

        current_avg.write({
            'average': avg_amount_avg
        })

        today  = self._get_tz_datetime(datetime.today())
        if last_day_date < today.date():
            next_date = last_day_date + relativedelta(months=1)

            self._update_avg(next_date, partner)

        if last_day_date >= today.date():
            partner.write({
                'pmfxp': avg_amount_avg / (partner.capacity),
                'pmf': avg_amount_avg
            })


    @api.model
    def update_all_daily_avg(self):
        today = self._get_tz_datetime(datetime.today())
        invoices = self.env['account.move'].search([
            ('state', '=', 'posted'),
            ('write_date', '>=', today.replace(hour=0, minute=0, second=0)),
            ('write_date', '<=', today.replace(hour=23, minute=59, second=59)),
            '|',
            ('type', '=', 'out_invoice'),
            ('type', '=', 'out_refund')])
        for invoice in invoices:
            last_day_date = self.env['account.move']._get_date_from_invoice(invoice)
            self._update_avg(last_day_date, invoice.partner_id)
