
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

class salesGoal(models.Model):
    _name = 'sales.goal'
    _description = 'Sales goal'

    name = fields.Char(string='Name', required=True, help='Set the name of the section')
    description = fields.Char(string='Description', required=True, help='Set the description of the section')
    parent_id = fields.Many2one(string='Parent goal', comodel_name='sales.goal', help='Set parent goal. Children will take invoice lines from parent.')
    section_type_id = fields.Many2one(string="Section type", comodel_name='sales.goal.section.type', help="Section type fot this goal. This may apply some conditions.")

    #domain = fields.Char(string='Conditions', help='Conditions for invoice lines to meet for this goal.')
    parent_domain = fields.Char(string='Parent conditions', help='Parent goal conditions for invoice lines to meet.', compute='_compute_parent_domain')
    all_domain = fields.Char(string='Conditions', help='All conditions for invoice lines to meet. It includes conditions from partent goals.')
    

    partner_id = fields.Many2one(string='Customer', help='Parner to meet conditions.', comodel_name='res.partner')
    product_category_id = fields.Many2one(string='Category', help='Product category to meet conditions.', comodel_name='product.category')
    sales_origin_id = fields.Many2one(string='Origin', help='Sales origin to meet conditions.', comodel_name='sales.origin')
    invoice_origin = fields.Selection([('sales', 'Sales'), ('reinvoice', 'Reincoiving')], string='Origin', default='sales', help='Invoice origin to meet conditions')

    show_name = fields.Boolean(default=True, help="Set active to false to hide the name as header on the sales report.")
    show_goal_pct = fields.Boolean(default=True, help="Set active to false to hide goal percentages on header.")
    show_sales_amount = fields.Boolean(default=True, help="Set active to false to hide sales amount on header.")
    show_total = fields.Boolean(default=True, help="Set active to false to hide the total amount as footer on the sales report.")

    goal_amount = fields.Float(string='Goal amount')

    structure = fields.Float(string='Structure', compute='_compute_structure')
    sales_percentage = fields.Float(string='Percentage', compute='_compute_sales_pct') 
    sales_at_date = fields.Monetary(string='Day', compute='_compute_sales_at_date')
    sales_total_week = fields.Monetary(string='Week', compute='_compute_sales_total_week')
    sales_total_month = fields.Monetary(string='Month', compute='_compute_sales_total_month')

    date_filter = fields.Date(string='At date', help='Set the date at you want to get the report.')

    period_month = fields.Integer(string='Month', help='Set the month when the goal applies.')
    period_year  = fields.Integer(string='Year', help='Set the year when the goal applies.')

    
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
