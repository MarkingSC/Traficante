
from dataclasses import field
import logging

from pkg_resources import require
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
    #description = fields.Char(string='Description', required=True, help='Set the description of the section')
    # meta padre
    parent_id = fields.Many2one(string='Group', comodel_name='sales.goal', help='Set parent goal. Children will take invoice lines from parent.')
    # metas hijas
    child_ids = fields.One2many('sales.goal', 'parent_id', string='Children')
    # tipo de sección relacionado con sales_goal_section_type
    section_type_id = fields.Many2one(
        string="Format", 
        comodel_name='sales.goal.section.type', 
        help="Format configuration for this goal on report.",
        required=True)
    # Monto de la meta
    goal_amount = fields.Float(string='Goal amount')
    # Secuencia en que aparece en el reporte
    sequence = fields.Integer(index=True, help="Gives the sequence order when displaying goals on list views and report.", default=1)

    # tipo de la meta, si es por cliente, producto, origen de venta u origen de factura
    type = fields.Selection(
        [
            ('group', 'Group'),
            ('salesperson', 'Sales Person'),
            ('customer', 'Customer'), 
            ('product', 'Product Category'), 
            ('s_origin', 'Sales Origin'), 
            ('i_origin', 'Invoice Origin')
            ], 
            string='Type', 
            default='salesperson', 
            help='Type of element which this goal is defined.',
            required=True)

    # Si se asocia a un ejecutivo
    sales_user_id = fields.Many2one(string='Sales Person', help='Sales person to meet conditions', comodel_name='res.users')
    # Si se asocia a un cliente
    partner_id = fields.Many2one(string='Customer', help='Parner to meet conditions.', comodel_name='res.partner')
    # Si se asocia a una categoría de producto
    product_category_ids = fields.Many2many(
        'product.category',
        'product_categories_per_sales_goal',
        'goal_id',
        'category_id',
        string = 'Categories')
    # Si se asocia a un origen de venta
    sales_origin_id = fields.Many2one(string='Sales Origin', help='Sales origin to meet conditions.', comodel_name='sales.origin')
    # Si se asocia a un origen de factura
    invoice_origin_id = fields.Many2one(string='Invoice Origin', help='Invoice origin to meet conditions.', comodel_name='invoice.origin')

    currency_id = fields.Many2one('res.currency', string='Currency')
    # Estructura: Porcentaje de la fila en función del total de ventas
    structure = fields.Float(string='Structure', compute='_compute_values', store=False)
    # Base para la estructura: Determina si la suma de las metas hijas será la base para su estructura
    structure_base = fields.Boolean(string="Structure base", help="Set true if the calculated strucuture will be used to calculate children structure.")
    # Porcentaje de venta
    sales_percentage = fields.Float(string='Percentage', compute='_compute_values', store=False) 
    # Ventas en la semana: Total de lunes a viernes truncado al mes, a la fecha en que se obtiene el reporte
    sales_total_week = fields.Monetary(string='Week', compute='_compute_values', store=False)
    # Ventas al mes: Total vendido en todo el mes hasta la fecha en que se obtiene el reporte
    sales_total_month = fields.Monetary(string='Month', compute='_compute_values', store=False)

    # Establece el día al que se quiere obtener el reporte
    date_filter = fields.Date(string='At date', help='Set the date at you want to get the report.')

    @api.depends('structure_base')
    def _validate_structure_base(self):
        _logger.info('**** ENTRA A _validate_structure_base *****')   
        existing = self.env['sales.goal'].search([('structure_base', '!=', False)], limit = 1)

        if existing and self.structure_base:
            self.structure_base = False
            raise ValidationError('Only one goal set as base structure is allowed.')


    def action_duplicate(self, month, year, duplicate_children):
        _logger.info('**** ENTRA A action_duplicate para: ' + str(self))  
        
        new_record = self.copy()
        if self.child_ids and duplicate_children:
            for child in self.child_ids:
                _logger.info('**** duplica el hijo: ' + str(child.name))  
                new_child = child.action_duplicate(month, year, duplicate_children)
                _logger.info('**** duplicó el hijo: ' + str(child.name))  
                new_child.parent_id = new_record
        
        new_record.period_month = month
        new_record.period_year = year
            
        return new_record

    def action_duplicate_goal_set_period(self):
        _logger.info("**** INICIA action_duplicate_goal_set_period")  
        active_ids = self.env.context.get('active_ids')

        if not active_ids:
            return ''

        return {
            'name': _('Duplicar metas'),
            'res_model': 'stock.picking.route.register',
            'view_mode': 'form',
            'view_id': self.env.ref('stock_traficante.stock_picking_delivery_route_date_multi').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

            
    def _get_years():
        year_list = []
        today = datetime.now()
        today_less10 = today.year - 10
        today_plus10 = today.year + 10

        for i in range(today_less10, today_plus10):
            year_list.append((str(i), str(i)))
        return year_list

    # Mes en que aplica la meta
    period_month = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                          ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), 
                          ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], 
                          string='Month', help='Set the month when the goal applies. Leve empty if it is a group.')
    # Año en que aplica la meta
    period_year  = fields.Selection(_get_years(), string='Year', help='Set the year when the goal applies. Leave empty if it is a group.')

    def write(self, values):
        """Override default Odoo write function and extend."""
        # Do your custom logic here
        _logger.info('**** ENTRA A write para cambiar el periodo de las metas hijas *****')   

        res = super(salesGoal, self).write(values)

        if 'period_year' in values or 'period_month' in values:
            for child in self.child_ids:
                child.period_month = self.period_month
                child.period_year = self.period_year

        return res

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
                lines = self.env['account.move.line'].search([('move_id.journal_id.type', '=', 'sale'), ('move_id.state', '=', 'posted'), ('product_id', '!=', False), ('move_id.date', '<=', today),('move_id.invoice_date', '>=', fdom), ('product_id.categ_id', 'in', record.product_category_ids.ids)])
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

            ##### Estructura si está marcada como la base
            if record.structure_base:
                _logger.info('**** Calcula la estructura base *****')
                _logger.info('**** goal.date_filter: ' + str(record.date_filter))
                goal_amt_sum = 0

                month_children = record.child_ids.filtered(lambda goal: int(goal.period_month) == int(record.date_filter.month) and int(goal.period_year) == int(record.date_filter.year))
                _logger.info('**** month_children: ' + str(month_children))
                for child in month_children:
                    _logger.info('**** Suma a la estructura base: ' +str(child.goal_amount))
                    goal_amt_sum += child.goal_amount

                _logger.info('**** Total de la estructura base: ' +str(goal_amt_sum))
                record.goal_amount = goal_amt_sum

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

            # estructura
            # Obtene el porcentaje de la estrucutura
            _logger.info('**** record.goal_amount : ' + str(record.goal_amount))

            if record.goal_amount > 0:
                base_goal_amount = self.env['sales.goal'].search([('structure_base', '!=', False)], limit = 1).goal_amount
                record.structure = record.goal_amount/base_goal_amount
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

    def action_set_duplicate(self):
        _logger.info("**** INICIA action_set_duplicate")  
        active_ids = self.env.context.get('active_ids')

        if not active_ids:
            return ''

        return {
            'name': _('Duplicate goals and groups'),
            'res_model': 'sales.goal.duplicate.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('traficante_sales_goals_report.sales_goal_duplicate_multi').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

class salesGoalDuplicate(models.TransientModel):
    _name = 'sales.goal.duplicate.wizard'
    _description = 'Duplicate goals'

    def _get_years():
        year_list = []
        today = datetime.now()
        today_less10 = today.year - 10
        today_plus10 = today.year + 10

        for i in range(today_less10, today_plus10):
            year_list.append((str(i), str(i)))
        return year_list

    # Mes en que aplica la meta
    period_month = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                          ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), 
                          ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], 
                          string='Month', help='Set the month when the goal applies. Leve empty if it is a group.')
    # Año en que aplica la meta
    period_year  = fields.Selection(_get_years(), string='Year', help='Set the year when the goal applies. Leave empty if it is a group.')

    duplicate_children = fields.Boolean(string="Duplicate children", help="Set true if you want to duplicate children also.")

    goal_ids = fields.Many2many("sales.goal",
                                         "sales_goal_duplicate_wizard_rel_transient",
                                         "wizard_id","goal_id",
                                         string="Goals", copy=False, readonly=True)

    # Función para obtener los datos del contexto incluidas las metas seleccionadas
    @api.model
    def default_get(self, fields):
        _logger.info("**** INICIA default_get")  

        rec = super(salesGoalDuplicate, self).default_get(fields)

        if self._context.get('params'):            
            _logger.info("***** self._context.get('params').get('id'): " + str (self._context.get('params').get('id')))  
            active_ids = self._context.get('params').get('id')
        else:
            _logger.info("***** self._context.get('active_ids'): " + str(self._context.get('active_ids')))  
            active_ids = self._context.get('active_ids')

        # Si aun no están asignadas las asigna a partir de los active_ids
        if not active_ids:
            return rec
        goals = self.env['sales.goal'].browse(active_ids)

        if 'goal_ids' not in rec:
            rec['goal_ids'] = [(6, 0, goals.ids)]
        return rec

    def action_duplicate(self):
        _logger.info("**** INICIA action_duplicate del wizard")  

        for record in self.goal_ids:
            record.action_duplicate(self.period_month, self.period_year, self.duplicate_children)

        # Una vez realizada la acción refresca la pantalla para ver los resultados
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


    