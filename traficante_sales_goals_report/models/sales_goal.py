
from dataclasses import field
import logging
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

    #Campo para activar/descativar las metas/secciones
    active = fields.Boolean('Active', default=True,
        help="By unchecking the active field, this goal/section will not be used.")

    # nombre del registro de la meta
    name = fields.Char(string='Name', required=True, help='Set the name of the section')
    # descripcion del registro de la meta
    description = fields.Char(string='Description', required=True, help='Set the description of the section')
    # meta padre
    parent_id = fields.Many2one(string='Parent goal', comodel_name='sales.goal', help='Set parent goal. Children will take invoice lines from parent.')
    # metas hijas
    child_ids = fields.One2many('sales.goal', 'parent_id', string='Child Goals')
    # tipo de sección relacionado con sales_goal_section_type
    section_type_id = fields.Many2one(string="Section type", comodel_name='sales.goal.section.type', help="Section type fot this goal. This may apply some conditions.")
    # Monto de la meta
    goal_amount = fields.Float(string='Goal amount')
    # Secuencia en que aparece en el reporte
    sequence = fields.Integer(index=True, help="Gives the sequence order when displaying goals on list views and report.", default=1)

    # tipo de la meta, si es por cliente, producto, origen de venta u origen de factura
    type = fields.Selection([('group', 'Group'),('salesperson', 'Sales Person'),('customer', 'Customer'), ('product', 'Product Category'), ('s_origin', 'Sales Origin'), ('i_origin', 'Invoice Origin')], string='Type', default='salesperson', help='Type of element which this goal is defined.')

    # Si se asocia a un ejecutivo
    sales_user_id = fields.Many2one(string='Sales Person', help='Sales person to meet conditions', comodel_name='res.users')
    # Si se asocia a un cliente
    partner_id = fields.Many2one(string='Customer', help='Parner to meet conditions.', comodel_name='res.partner')
    # Si se asocia a una categoría de producto
    product_category_id = fields.Many2one(string='Category', help='Product category to meet conditions.', comodel_name='product.category')
    # Si se asocia a un origen de venta
    sales_origin_id = fields.Many2one(string='Sales Origin', help='Sales origin to meet conditions.', comodel_name='sales.origin')
    # Si se asocia a un origen de factura
    invoice_origin_id = fields.Many2one(string='Invoice Origin', help='Invoice origin to meet conditions.', comodel_name='invoice.origin')

    # si se muestra el nombre en el encabezado
    show_name = fields.Boolean(default=True, help="Set active to false to hide the name as header on the sales report.")
    # Si se muestra el porcentaje de la meta en el encabezado
    show_goal_pct = fields.Boolean(default=True, help="Set active to false to hide goal percentages on header.")
    # Si se muestra el monto de la venta en el encabezado
    show_sales_amount = fields.Boolean(default=True, help="Set active to false to hide sales amount on header.")
    # Si se muestra el total de la venta en el footer
    show_total = fields.Boolean(default=True, help="Set active to false to hide the total amount as footer on the sales report.")


    # Estructura: Porcentaje de la fila en función del total de ventas
    structure = fields.Float(string='Structure', compute='_compute_structure', store=False)
    # Porcentaje de venta
    sales_percentage = fields.Float(string='Percentage', compute='_compute_sales_pct', store=False) 
    # Ventas a la fecha: Total vendido en el día en que se obtiene el reporte
    sales_at_date = fields.Float(string='Day', compute='_compute_sales_at_date', store=False)
    # Ventas en la semana: Total de lunes a viernes truncado al mes, a la fecha en que se obtiene el reporte
    sales_total_week = fields.Float(string='Week', compute='_compute_sales_total_week', store=False)
    # Ventas al mes: Total vendido en todo el mes hasta la fecha en que se obtiene el reporte
    sales_total_month = fields.Float(string='Month', compute='_compute_sales_total_month', store=False)

    # Establece el día al que se quiere obtener el reporte
    date_filter = fields.Date(string='At date', help='Set the date at you want to get the report.')

    # Mes en que aplica la meta
    period_month = fields.Integer(string='Month', help='Set the month when the goal applies. Leve empty if it is a group.')
    # Año en que aplica la meta
    period_year  = fields.Integer(string='Year', help='Set the year when the goal applies. Leve empty if it is a group.')


    @api.depends('parent_id')
    def _get_move_lines(self):
        for record in self:

            today = datetime.now()
            fdom = ''
            # primer día del mes
            if record.date_filter:
                fdom = record.date_filter.replace(day=1)
            else:
                fdom = datetime.now().replace(day=1)

            lines = []
            if record.type == 'salesperson':
                lines = self.env['account.move.line'].search([('date', '<=', today),('date', '>=', fdom), ('move_id.invoice_user_id', '=', record.sales_user_id)])
            elif record.type == 'customer':
                lines = self.env['account.move.line'].search([('date', '<=', today),('date', '>=', fdom), ('partner_id', '=', record.partner_id)])
            elif record.type == 'product':
                lines = self.env['account.move.line'].search([('date', '<=', today),('date', '>=', fdom), ('product_id.categ_id', '=', record.product_category_id)])
            elif record.type == 's_origin':
                orders = self.env['sale.order'].search([('sales_origin_id', '=', record.sales_origin_id)])
                orders_names = orders.read('name')
                _logger.info('**** orders_names: ' + str(orders_names))

                lines = self.env['account.move.line'].search([('date', '<=', today),('date', '>=', fdom), ('move_id.invoice_origin', 'in', orders_names)])
            elif record.type == 'i_origin':
                lines = self.env['account.move.line'].search([('date', '<=', today),('date', '>=', fdom), ('move_id.invoice_origin_id', '=', record.invoice_origin_id)])
            else: 
                lines = []

        return lines

    def _compute_values(self):
        for record in self:

            record_lines = record._get_move_lines()

            # total del mes hasta la fecha
            total_month = 0
            today = datetime.now()
            if record.date_filter:
                today = record.date_filter

            _, days_month = calendar.monthrange(today.year, today.month)
            first_day = datetime(today.year, today.month, 1)
            last_day = datetime(today.year, today.month, days_month)

            week_lines = invoice_lines.search([('date', '<=', last_day), ('date', '>=', first_day)])

            for line in week_lines:
                total_month += line.amount_currency

            record.sales_total_month = total_month

            # porcentaje de ventas
            if record.goal_amount:
                record.sales_percentage = record.sales_total_month/record.goal_amount
            else:
                record.sales_percentage = 0

            # total de la semana
            total_week = 0
            if record.all_domain:
                invoice_lines = self.env['account.move.line'].search(eval(record.all_domain))

                today = datetime.now()
                if record.date_filter:
                    today = record.date_filter
                
                timedelta_monday = timedelta(today.weekday())
                timedelta_friday = timedelta(4-today.weekday())
                last_monday = today - timedelta_monday
                next_friday = today + timedelta_friday

                week_lines = invoice_lines.search([('date', '<=', next_friday), ('date', '>=', last_monday)])

                for line in week_lines:
                    total_week += line.amount_currency

            record.sales_total_week = total_week

            # total a la fecha
            total_at_date = 0
            if record.all_domain:
                fdom = ''
                # primer día del mes
                if record.date_filter:
                    fdom = record.date_filter.replace(day=1)
                else:
                    fdom = datetime.now().replace(day=1)

                _logger.info('**** record.all_domain: ' + str(record.all_domain))
                # busca todas las lineas de factura que coincidan con los filtros
                invoice_lines = self.env['account.move.line'].search(eval(record.all_domain)+[('date', '>=', fdom)])
                # Obtiene las lineas que son solo de la fecha del reporte
                invoice_lines = invoice_lines.search([('date', '=', record.date_filter)])

                for line in invoice_lines:
                    total_at_date += line.amount_currency
            
            # setea el monto en el registro de la meta
            record.sales_at_date = total_at_date

            # estructura
            total_amount = 0
            if record.all_domain:
                fdom = ''
                # primer día del mes
                if record.date_filter:
                    fdom = record.date_filter.replace(day=1)
                else:
                    fdom = datetime.now().replace(day=1)

                _logger.info('**** record.all_domain: ' + str(record.all_domain))
                # busca todas las lineas de factura que coincidan con los filtros
                all_lines = self.env['account.move.line'].search(eval(record.all_domain)+[('date', '>=', fdom)])
                # Hace la suma de los montos de las líneas
                for line in all_lines:
                    total_amount += line.amount_currency

            # Obtene el porcentaje de la estrucutura
            if record.goal_amount > 0:
                record.structure = total_amount/record.goal_amount
            else:
                record.structure = 0