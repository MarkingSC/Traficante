from odoo import models, fields, api, _, exceptions
from datetime import datetime, time, timedelta
import logging

_logger = logging.getLogger(__name__)

class SalesGoalReportWizard(models.TransientModel):
    _name = 'sales.goals.report.wizard'

    date_filter = fields.Date(string='At date', help='Set the date at you want to get the report.', default = datetime.today(), store = True)

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_filter': self.date_filter
            },
        }

        return self.env.ref('traficante_sales_goals_report.action_report_sales_goals').report_action(self, data=data)

class SalesGoalReport(models.AbstractModel):
    _name = 'report.sales.goals.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, goals):
        _logger.info('**** Inicio generate_xlsx_report ****') 

        date_filter = data['form']['date_filter'] 
        _logger.info('**** date_filter: ' + str(date_filter))  
        date_filter = datetime.strptime(date_filter, '%Y-%m-%d')

        company_format = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bold': True})
        header_col_format = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bold': True, 'bg_color': '#DB3545', 'font_color': 'white'})
        align_center = workbook.add_format({'font_size': 10, 'align': 'vcenter'})

        sheet = workbook.add_worksheet('Ventas mes')

        today = datetime.now()
        if date_filter:
            today = date_filter
        today = datetime.combine(today, time.max)

        sheet.write(1,0, 'Compañia', company_format)
        sheet.write(2,0, 'REPORTE DIARIO Y ACUMULADO DE ' + today.strftime("%B") + ' ' + today.strftime("%Y") , align_center)
        sheet.write(3,0, '(Cifras en pesos)', align_center)

        sheet.write(4,0, str(today.day) + (today.strftime(" de %B del %Y")), align_center)

        sheet.write(5,4, (today.strftime("%A")))

        sheet.write(6,0, 'DIA/MES', header_col_format)
        sheet.write(6,1, 'META', header_col_format)
        sheet.write(6,2, 'ESTRUCTURA', header_col_format)
        sheet.write(6,3, 'PORCENTAJE', header_col_format)
        sheet.write(6,4, str(today.day), header_col_format)

        timedelta_monday = timedelta(today.weekday())
        last_monday = today - timedelta_monday
        last_monday = datetime.combine(last_monday, time.min)

        sheet.write(6,5, ('Total Semana (' + str(last_monday.day) + last_monday.strftime(" de %B al ") + str(today.day) + ')') , header_col_format)
        sheet.write(6,6, (today.strftime('%B')), header_col_format)

        # busca las metas que se van a mostrar en el reporte
        goals = self.env['sales.goal'].search([
            ('active', '=', True),
            '|',
            ('type', '=', 'group'), 
            '&',
            ('period_month', '=', False), 
            ('period_year', '=', False),
            ('parent_id', '=', False)], order='sequence')

        row = 7
        for goal in goals:
            row = self.print_goal_row(row, sheet, goal, date_filter)

        _logger.info('**** Fin generate_xlsx_report ****')   

    def print_goal_row(self, row, sheet, goal, date_filter):
        _logger.info('**** Inicio print_goal_row ****')   
        _logger.info('**** Meta: ' + str(goal.name))

        goal.date_filter = date_filter
        date_year = date_filter.year
        date_month = date_filter.month

        # ejecuta la obtención de los datos
        goal._compute_values()

        if goal.show_name != False:
            _logger.info('**** goal.show_name ****')   
            sheet.write(row,0, goal.name)

            if goal.show_goal_pct != False:
                _logger.info('**** goal.show_goal_pct ****')   
                sheet.write(row,2, str(round((goal.structure * 100), 2))+'%')
                sheet.write(row,3, str(round((goal.sales_percentage * 100), 2))+'%')
            
            if goal.show_sales_amount != False:
                _logger.info('**** goal.show_sales_amount ****')   
                sheet.write(row,4, str("${:,.2f}".format(goal.sales_at_date)))
                sheet.write(row,5, str("${:,.2f}".format(goal.sales_total_week)))
                sheet.write(row,6, str("${:,.2f}".format(goal.sales_total_month)))
                sheet.write(row,1, str("${:,.2f}".format(goal.goal_amount)))

            row += 1

        if goal.child_ids != False:
            _logger.info('**** goal.child_ids ****')   
            filtered_childs = goal.child_ids.filtered(lambda child: child.active == True and (
                (child.type == 'group') or (child.period_month == int(date_month) and child.period_year == int(date_year)))
                )
            for child in filtered_childs:
                row = self.print_goal_row(row, sheet, child, date_filter)

        if goal.show_total != False:
            _logger.info('**** goal.show_total ****')   

            total_goal_amount = 0
            total_structure = 0
            total_sales_percentage = 0
            total_sales_at_date = 0
            total_sales_total_week = 0
            total_sales_total_month = 0
            
            if goal.child_ids != False:
                _logger.info('**** goal.child_ids ****')   
                for child in goal.child_ids:
                    
                    total_goal_amount += child.goal_amount
                    total_structure += child.structure
                    total_sales_percentage += child.sales_percentage
                    total_sales_at_date += child.sales_at_date
                    total_sales_total_week += child.sales_total_week
                    total_sales_total_month += child.sales_total_month
            else:
                total_goal_amount = goal.goal_amount
                total_structure = goal.structure
                total_sales_percentage = goal.sales_percentage
                total_sales_at_date = goal.sales_at_date
                total_sales_total_week = goal.sales_total_week
                total_sales_total_month = goal.sales_total_month
            

            sheet.write(row,0, 'TOTAL')
            sheet.write(row,1, str("${:,.2f}".format(total_goal_amount)))
            sheet.write(row,2, str(round((total_structure * 100), 2))+'%')
            sheet.write(row,3, str(round((total_sales_percentage * 100), 2))+'%')
            sheet.write(row,4, str("${:,.2f}".format(total_sales_at_date)))
            sheet.write(row,5, str("${:,.2f}".format(total_sales_total_week)))
            sheet.write(row,6, str("${:,.2f}".format(total_sales_total_month)))

        _logger.info('**** Fin print_goal_row ****')   
        return row