from odoo import models, fields, api, _, exceptions
from datetime import datetime, time, timedelta, date
import locale
import logging

_logger = logging.getLogger(__name__)

class SalesGoalReportWizard(models.TransientModel):
    _name = 'sales.goals.report.wizard'

    date_start = fields.Date(string='From date', help='Set the date from want to get the report.', default = datetime.today().replace(day=1))
    date_filter = fields.Date(string='To date', help='Set the date until you want to get the report.', default = datetime.today())
    full_period = fields.Boolean(default=True, help="Check to show all saler per day since the first day in month until the specified date.")

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_filter': self.date_filter,
                'date_start': self.date_start,
                'full_period': self.full_period
            },
        }

        return self.env.ref('traficante_sales_goals_report.action_report_sales_goals').report_action(self, data=data)

class SalesGoalReport(models.AbstractModel):
    _name = 'report.sales.goals.report'
    _inherit = 'report.report_xlsx.abstract'

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def generate_xlsx_report(self, workbook, data, goals):
        _logger.info('**** Inicio generate_xlsx_report ****') 

        user_lang = self.env.context['lang'] + '.utf8'

        locale.setlocale(locale.LC_TIME, user_lang)

        date_filter = data['form']['date_filter'] 
        _logger.info('**** date_filter: ' + str(date_filter))  
        date_filter = datetime.strptime(date_filter, '%Y-%m-%d')

        date_start = data['form']['date_start'] 
        _logger.info('**** date_start: ' + str(date_start))  
        date_start = datetime.strptime(date_start, '%Y-%m-%d')

        full_period = data['form']['full_period'] 
        _logger.info('**** full_period: ' + str(full_period))  

        company_format = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bold': True})
        header_col_format = workbook.add_format(
            {'font_size': 10, 
            'align': 'vcenter', 
            'bold': True, 
            'bg_color': '#DB3545', 
            'font_color': 'white',
            'border': 1})
        align_center = workbook.add_format({'font_size': 10, 'align': 'vcenter'})

        sheet = workbook.add_worksheet('Ventas ' + date_filter.strftime("%B"))

        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 3, 15)

        #today = datetime.now()
        #if date_filter:
        #    today = date_filter
        date_filter = datetime.combine(date_filter, time.max)

        sheet.write(1,0, self.env.company.name, company_format)
        sheet.write(2,0, 'REPORTE DIARIO Y ACUMULADO DE ' + date_filter.strftime("%B").upper() + ' ' + date_filter.strftime("%Y") , align_center)
        sheet.write(3,0, '(Cifras en pesos)', align_center)

        sheet.write(4,0, str(date_filter.day) + (date_filter.strftime(" de %B del %Y")), align_center)

        #sheet.write(5,4, (date_filter.strftime("%A")))

        sheet.write(6,0, 'DIA/MES', header_col_format)
        sheet.write(6,1, 'META', header_col_format)
        sheet.write(6,2, 'ESTRUCTURA', header_col_format)
        sheet.write(6,3, 'PORCENTAJE', header_col_format)
        #sheet.write(6,4, str(date_filter.day), header_col_format)

        timedelta_monday = timedelta(date_filter.weekday())
        last_monday = date_filter - timedelta_monday
        last_monday = datetime.combine(last_monday, time.min)

        # Establece la fecha inicial al primer día del mes, pero si hay una fecha inicial entonces usa esa
        first_day = datetime.combine(date(date_filter.year, date_filter.month, 1), time.min)
        if date_start:
            first_day = datetime.combine(date_start, time.min)

        if full_period:

            # Itera los días entre el rango de fechas desde el inicio del mes hasta la fecha de obtención del reporte
            column = 4

            for day in self.daterange(first_day, date_filter + timedelta(days=1) ):

                sheet.write(5, column, str(day.strftime("%A")))
                sheet.write(6, column, str(day.day), header_col_format)

                column += 1
            # fin de la iteración

            sheet.write(6,column, ('Total Semana (' + str(last_monday.day) + last_monday.strftime(" de %B al ") + str(date_filter.day) + ')') , header_col_format)
            sheet.write(6,column+1, (date_filter.strftime('%B')), header_col_format)

            
            sheet.set_column(4, column-1, 10)
            sheet.set_column(column, column+1, 20)
        else:
            sheet.write(5, 4, str(date_filter.strftime("%A")))
            sheet.write(6, 4, str(date_filter.day), header_col_format)

            sheet.write(6, 5, ('Total Semana (' + str(last_monday.day) + last_monday.strftime(" de %B al ") + str(date_filter.day) + ')') , header_col_format)
            sheet.write(6, 6, (date_filter.strftime('%B')), header_col_format)

            sheet.set_column(4, 4, 10)
            sheet.set_column(5, 6, 20)

        goals = self.env['sales.goal'].search([
            ('active', '=', True),
            ('parent_id', '=', False)], order='sequence')

        tree_level = 1
        row = 7
        for goal in goals:
            row = self.print_goal_row(row, workbook, sheet, goal, first_day, date_filter, full_period, tree_level)

        _logger.info('**** Fin generate_xlsx_report ****')   

    def print_goal_row(self, row, workbook, sheet, goal, date_start, date_filter, full_period, tree_level):
        _logger.info('**** Inicio print_goal_row ****')   
        _logger.info('**** Meta: ' + str(goal.name))

        
        # Add a number format for cells with money and color format
        money_format = workbook.add_format(
            {'num_format': '$#,##0.00', 
            'bg_color': goal.section_type_id.bg_color, 
            'font_color': goal.section_type_id.font_color, 
            'border': 1})
        bg_format = workbook.add_format(
            {'bg_color': goal.section_type_id.bg_color, 
            'font_color': goal.section_type_id.font_color, 
            'border': 1})

        goal.date_filter = date_filter
        date_year = date_filter.year
        date_month = date_filter.month

        first_day = datetime.combine(date_start, time.min)

        # ejecuta la obtención de los datos
        _logger.info('**** Pasa a _compute_values ****')   
        goal._compute_values()

        if goal.section_type_id.show_name != False:
            _logger.info('**** goal.section_type_id.show_name ****') 
            tab_prefix = '';  
            for i in range(1, tree_level):
                tab_prefix += '    '
            sheet.write(row,0, tab_prefix + goal.name, bg_format)

        if goal.section_type_id.show_goal_pct != False:
            _logger.info('**** goal.section_type_id.show_goal_pct ****')   
            sheet.write(row,2, str(round((goal.structure * 100), 2))+'%', bg_format)
            sheet.write(row,3, str(round((goal.sales_percentage * 100), 2))+'%', bg_format)
            
        if goal.section_type_id.show_sales_amount != False:
            _logger.info('**** goal.section_type_id.show_sales_amount ****')   

            if full_period:
                # Itera los días entre el rango de fechas desde el inicio del mes hasta la fecha de obtención del reporte
                column = 4

                for day in self.daterange(first_day, date_filter + timedelta(days=1) ):
                    _logger.info('**** Calculando ventas al: ' + str(day.strftime("%d-%m-%Y")))
                    day_sales = goal._get_on_date(day)
                    _logger.info('**** Ventas del dia: ' + str(day_sales))                        

                    sheet.write_number(row,column, float(day_sales), money_format)

                    column += 1
                # fin de la iteración

                sheet.write_number(row, column, float(goal.sales_total_week), money_format)
                sheet.write_number(row, column+1, float(goal.sales_total_month), money_format)
            else:
                day_sales = goal._get_on_date(date_filter)
                sheet.write_number(row, 4, float(day_sales), money_format)

                sheet.write_number(row, 5, float(goal.sales_total_week), money_format)
                sheet.write_number(row, 6, float(goal.sales_total_month), money_format)

            sheet.write_number(row,1, float(goal.goal_amount), money_format)
        
        if goal.section_type_id.show_name or goal.section_type_id.show_goal_pct or goal.section_type_id.show_sales_amount:
            row += 1

        ### Terminó de pintar la fila de la meta y va por las de las hijas

        if goal.child_ids != False:
            _logger.info('**** goal.child_ids ****')   
            filtered_childs = goal.child_ids.filtered(lambda child: child.active == True and (
                (child.type == 'group') or (int(child.period_month) == int(date_month) and int(child.period_year) == int(date_year)))
                )

            tree_level += 1
            for child in filtered_childs:
                row = self.print_goal_row(row, workbook, sheet, child, date_start, date_filter, full_period, tree_level)

        ### Imprime la fila de totales
        if goal.section_type_id.show_total != False:
            _logger.info('**** goal.section_type_id.show_total ****')   

            total_sales_total_week = 0
            total_sales_total_month = 0
            
            if goal.child_ids != False:
                _logger.info('**** goal.child_ids ****')   
                for child in goal.child_ids:
                    
                    total_sales_total_week += child.sales_total_week
                    total_sales_total_month += child.sales_total_month
            else:
                total_sales_total_week = goal.sales_total_week
                total_sales_total_month = goal.sales_total_month
            
            if full_period:
                # Itera los días entre el rango de fechas desde el inicio del mes hasta la fecha de obtención del reporte
                column = 4

                for day in self.daterange(first_day, date_filter + timedelta(days=1) ):
                    _logger.info('**** Obteniendo total al: ' + str(day.strftime("%d-%m-%Y")))
                    total_day_sales = goal._get_on_date(day, False)
                    _logger.info('**** Total del día: ' + str(total_day_sales))
                    sheet.write_number(row,column, float(total_day_sales), money_format)

                    column += 1
                # fin de la iteración

                sheet.write_number(row, column, float(total_sales_total_week), money_format)
                sheet.write_number(row, column+1, float(total_sales_total_month), money_format)
            else:
                total_day_sales = goal._get_on_date(date_filter)
                sheet.write_number(row, 4, float(total_day_sales), money_format)

                sheet.write_number(row, 5, float(total_sales_total_week), money_format)
                sheet.write_number(row, 6, float(total_sales_total_month), money_format)

            sheet.write(row,0, goal.section_type_id.total_row_name, bg_format)

            sheet.write_number(row,1, goal.goal_amount, money_format)

            base_goal_amount = self.env['sales.goal'].search([('structure_base', '!=', False)], limit = 1).goal_amount
            total_structure = goal.goal_amount/base_goal_amount
            sheet.write(row,2, str(round((total_structure * 100), 2))+'%', bg_format)

            if goal.goal_amount:
                total_sales_percentage = total_sales_total_month/goal.goal_amount
            else:
                 total_sales_percentage = 0
            sheet.write(row,3, str(round((total_sales_percentage * 100), 2))+'%', bg_format)

            row += 1
            

        _logger.info('**** Fin print_goal_row ****')   
        return row