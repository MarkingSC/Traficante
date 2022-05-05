
from dataclasses import field
import logging
from odoo import models, fields, api, _, exceptions
import odoo
from datetime import timedelta, datetime, date, time
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

    currency_id = fields.Many2one('res.currency', string='Currency')
    # Estructura: Porcentaje de la fila en función del total de ventas
    structure = fields.Float(string='Structure', compute='_compute_values', store=False)
    # Porcentaje de venta
    sales_percentage = fields.Float(string='Percentage', compute='_compute_values', store=False) 
    # Ventas a la fecha: Total vendido en el día en que se obtiene el reporte
    sales_on_date = fields.Monetary(string='Day', compute='_compute_values', store=False)
    # Ventas en la semana: Total de lunes a viernes truncado al mes, a la fecha en que se obtiene el reporte
    sales_total_week = fields.Monetary(string='Week', compute='_compute_values', store=False)
    # Ventas al mes: Total vendido en todo el mes hasta la fecha en que se obtiene el reporte
    sales_total_month = fields.Monetary(string='Month', compute='_compute_values', store=False)

    # Establece el día al que se quiere obtener el reporte
    date_filter = fields.Date(string='At date', help='Set the date at you want to get the report.')

    # Mes en que aplica la meta
    period_month = fields.Integer(string='Month', help='Set the month when the goal applies. Leve empty if it is a group.')
    # Año en que aplica la meta
    period_year  = fields.Integer(string='Year', help='Set the year when the goal applies. Leve empty if it is a group.')


    def _get_move_lines(self):
        
        for record in self:

            _logger.info('**** ENTRA A _get_move_lines de la meta:' + str(record.name))   

            today = datetime.now()
            fdom = ''
            # primer día del mes
            if record.date_filter:
                fdom = record.date_filter.replace(day=1)
            else:
                fdom = datetime.now().replace(day=1)

            _logger.info('**** PRIMER DIA DEL MES: ' + str(fdom))

            lines = self.env['account.move.line']
            if record.type == 'salesperson':
                lines = self.env['account.move.line'].search([('move_id.journal_id.type', '=', 'sale'), ('move_id.state', '=', 'posted'), ('product_id', '!=', False), ('move_id.date', '<=', today),('move_id.invoice_date', '>=', fdom), ('move_id.invoice_user_id', '=', record.sales_user_id.id)])
            elif record.type == 'customer':
                lines = self.env['account.move.line'].search([('move_id.journal_id.type', '=', 'sale'), ('move_id.state', '=', 'posted'), ('product_id', '!=', False), ('move_id.date', '<=', today),('move_id.invoice_date', '>=', fdom), ('partner_id', '=', record.partner_id.id)])
            elif record.type == 'product':
                lines = self.env['account.move.line'].search([('move_id.journal_id.type', '=', 'sale'), ('move_id.state', '=', 'posted'), ('product_id', '!=', False), ('move_id.date', '<=', today),('move_id.invoice_date', '>=', fdom), ('product_id.categ_id', '=', record.product_category_id.id)])
            elif record.type == 's_origin':
                orders = self.env['sale.order'].search([('sales_origin_id', '=', record.sales_origin_id)])
                orders_names = orders.read('name')
                _logger.info('**** orders_names: ' + str(orders_names))

                lines = self.env['account.move.line'].search([('move_id.journal_id.type', '=', 'sale'), ('move_id.state', '=', 'posted'), ('product_id', '!=', False), ('move_id.date', '<=', today),('move_id.invoice_date', '>=', fdom), ('move_id.invoice_origin', 'in', orders_names)])
            elif record.type == 'i_origin':
                lines = self.env['account.move.line'].search([('move_id.journal_id.type', '=', 'sale'), ('move_id.state', '=', 'posted'), ('product_id', '!=', False), ('move_id.date', '<=', today),('move_id.invoice_date', '>=', fdom), ('move_id.invoice_origin_id', '=', record.invoice_origin_id.id)])
            
            elif record.type == 'group':
                if record.child_ids:
                    for child in record.child_ids:
                        child_lines = child._get_move_lines()    

                        _logger.info('**** child_lines: ' + str(child_lines))
                        _logger.info('**** child_lines type: ' + str(type(child_lines)))
                        
                        _logger.info('**** lines: ' + str(lines))    
                        _logger.info('**** lines type: ' + str(type(lines)))    

                        lines = lines | child._get_move_lines()    
                        
                        _logger.info('**** child_lines type: ' + str(type(child_lines)))
                        _logger.info('**** lines type: ' + str(type(lines)))               
            else: 
                lines = ()

            _logger.info('**** LINEAS: ' + str(lines))

        _logger.info('**** TERMINA _get_move_lines ****')   
        return lines

    def _compute_values(self):
        _logger.info('**** INICIA _compute_values ****')   
        for record in self:

            invoice_lines = record._get_move_lines()
            _logger.info('**** LINEAS: ' + str(invoice_lines))

            #####
            # total del mes hasta la fecha
            total_month = 0
            today = datetime.now()
            if record.date_filter:
                today = record.date_filter
            
            today = datetime.combine(today, time.max)

            _logger.info('**** DÍA DEL REPORTE: ' + str(today))

            _, days_month = calendar.monthrange(today.year, today.month)
            first_day = datetime.combine(date(today.year, today.month, 1), time.min)
            last_day = datetime.combine(date(today.year, today.month, days_month), time.max)

            _logger.info('**** PRIMER DIA DEL MES: ' + str(first_day))
            _logger.info('**** ULTIMO DIA DEL MES: ' + str(last_day))

            if invoice_lines:
                month_lines = invoice_lines.filtered(lambda line: datetime.combine(line.move_id.date, time.min) <= last_day and datetime.combine(line.move_id.date, time.min) >= first_day)

                _logger.info('**** month_lines: ' + str(month_lines))

                for line in month_lines:    
                    total_month += abs(line.price_total)

            _logger.info('**** total_month: ' + str(total_month))
            record.sales_total_month = total_month
            _logger.info('**** record.sales_total_month: ' + str(record.sales_total_month))
            _logger.info('**** record.goal_amount: ' + str(record.goal_amount))

            #####
            # porcentaje de ventas
            if record.goal_amount:
                record.sales_percentage = record.sales_total_month/record.goal_amount
            else:
                record.sales_percentage = 0

            _logger.info('**** record.sales_percentage : ' + str(record.sales_percentage ))

            #####   
            # total de la semana
            total_week = 0
            
            timedelta_monday = timedelta(today.weekday())
            last_monday = today - timedelta_monday
            last_monday = datetime.combine(last_monday, time.min)

            _logger.info('**** last_monday : ' + str(last_monday))

            if invoice_lines:
                week_lines = invoice_lines.filtered(lambda line: datetime.combine(line.move_id.date, time.min) <= today and datetime.combine(line.move_id.date, time.min) >= last_monday)

                for line in week_lines:
                    _logger.info('**** line.move_id.name : ' + str(line.move_id.name))
                    _logger.info('**** abs(line.price_total) : ' + str(abs(line.price_total)))
                    total_week += abs(line.price_total)

            record.sales_total_week = total_week
            _logger.info('**** record.sales_total_week : ' + str(record.sales_total_week))

            #####
            # total vendido en la fecha
            # setea el monto en el registro de la meta
            record.sales_on_date = record._get_on_date(today)

            _logger.info('**** record.sales_on_date : ' + str(record.sales_on_date))

            #####
            # estructura
            # Obtene el porcentaje de la estrucutura
            _logger.info('**** record.goal_amount : ' + str(record.goal_amount))

            if record.goal_amount > 0:
                record.structure = record.sales_total_month/record.goal_amount
            else:
                record.structure = 0

            _logger.info('**** record.structure : ' + str(record.structure))
        
        _logger.info('**** TERMINA _compute_values ****')   

    # Función para obtener el monto vendido en X fecha para self meta
    def _get_on_date(self, filter_date):
        for record in self:

            invoice_lines = record._get_move_lines()
            filter_date = datetime.combine(filter_date, time.min)

            total_on_date = 0
                
            if invoice_lines:
                lines_on_date = invoice_lines.filtered(lambda line: datetime.combine(line.move_id.date, time.min) == filter_date)

                for line in lines_on_date:
                    total_on_date += abs(line.price_total)
                
            return total_on_date