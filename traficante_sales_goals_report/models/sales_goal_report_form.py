
import logging
from typing_extensions import Required
from odoo import models, fields, api, _, exceptions
import odoo
from datetime import timedelta, datetime
import calendar
import pytz
from odoo.exceptions import AccessError, UserError, ValidationError

datetime.today()

_logger = logging.getLogger(__name__)

class salesGoalReportForm(models.TransientModel):

    _name = 'sales.goal.report.form'
    _description = 'Sales goal report form'

    report_date = fields.Date(string='Date to get the report.')
    
    @api.depends('parent_id', 'section_type_id')
    def _compute_parent_domain(self):
        for record in self:
            if record.parent_id:
                all_domain = record._compute_parent_domain() + record.parent_id.section_type_id.domain
            else:
                all_domain = record.section_type_id.domain
            
            record.all_dommain = all_domain

    @api.depends('goal_ammount')
    def _compute_structure(self):
        for record in self:

            all_lines = self.env['account.move.line'].search([])
            total_amount = 0
            for line in all_lines:
                total_amount += line.amount_currency

            record.structure = record.goal_amount/total_amount


    @api.depends('date_filter')
    def _compute_sales_at_date(self):
        for record in self:
            invoice_lines = self.env['account.move.line'].search(record.all_domain)
            record.sales_at_date = invoice_lines.search([('date', '=', record.date_filter)])

    @api.depends('date_filter')
    def _compute_sales_total_week(self):
        for record in self:
            invoice_lines = self.env['account.move.line'].search(record.all_domain)

            today = record.date_filter
            timedelta_monday = datetime.timedelta(today.weekday())
            timedelta_friday = datetime.timedelta(4-today.weekday())
            last_monday = today - timedelta_monday
            next_friday = today + timedelta_friday

            week_lines = invoice_lines.search([('date', '<=', next_friday), ('date', '>', last_monday)])

            total_amount = 0
            for line in week_lines:
                total_amount += line.amount_currency

            record.sales_total_week = total_amount


    @api.depends('date_filter')
    def _compute_sales_total_month(self):
        for record in self:
            invoice_lines = self.env['account.move.line'].search(record.all_domain)

            today = record.date_filter
            _, days_month = calendar.monthrange(today.year, today.month)
            first_day = datetime.datetime(today.year, today.month, 1)
            last_day = datetime.datetime(today.year, today.month, days_month)

            week_lines = invoice_lines.search([('date', '<=', last_day), ('date', '>', first_day)])

            total_amount = 0
            for line in week_lines:
                total_amount += line.amount_currency

            record.sales_total_month = total_amount

    @api.depends('sales_total_month', 'goal_amount')
    def _compute_sales_pct(self):
        for record in self:
            record.sales_pct = record.sales_total_month/record.goal_amount
