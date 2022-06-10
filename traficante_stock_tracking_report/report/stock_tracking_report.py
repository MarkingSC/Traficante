import base64
from email.policy import default
import io
from odoo import models, fields, api, _, exceptions
from datetime import date, datetime, time, timedelta
import logging

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class StockTrackingReportWizard(models.TransientModel):
    _name = 'stock.tracking.report.wizard'

    date_from = fields.Date(string='From date', help='Set the date from you want to get the report.', default = datetime.today().replace(day=1))
    date_to = fields.Date(string='To date', help='Set the date until you want to get the report.', default = datetime.today())

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
        }

        return self.env.ref('traficante_stock_tracking_report.stock_tracking_report_xlsx').report_action(self, data=data)


class stockTrackingReport(models.AbstractModel):
    _name = 'report.stock.tracking.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, products):
        _logger.info('**** Inicio generate_xlsx_report ****') 

        if 'form' in data:
            report_date_from = data['form']['date_from']
            report_date_from = datetime.strptime(report_date_from, '%Y-%m-%d')
            report_date_from = datetime.combine(report_date_from, time.min)

            report_date_to = data['form']['date_to']
            report_date_to = datetime.strptime(report_date_to, '%Y-%m-%d')
            report_date_to = datetime.combine(report_date_to, time.max)

        today = date.today()

        # Add a number format for cells with money and color format
        money_format = workbook.add_format(
            {'num_format': '$#,##0.00'})
        
        percent_format = workbook.add_format(
            {'num_format': '#,##0.00%'})
        

        # Definición de estilos del excel
        company_format = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bold': True})
        header_col_format = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bold': True})
        header_col_format_gray = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bg_color': '#c2c2c2', 'bold': True})

        sheet = workbook.add_worksheet('Trazabilidad ' + today.strftime( '%d%m%y'))
        # sheet.set_column(0, 4, 200)

        # Imprime los encabezados del excel
        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 30)
        sheet.set_column(2, 2, 10)
        sheet.set_column(3, 6, 20)
        sheet.set_column(7, 8, 30)
        sheet.set_column(9, 10, 20)
        sheet.set_column(11, 13, 10)

        #sheet.insert_image('A1', self.env.user.company_id.logo)
        sheet.merge_range('C3:H3', 'REPORTE DE TRAZABILIDAD DEL ' + str(report_date_from.strftime('%d/%m/%Y')) + ' al ' + str(report_date_to.strftime('%d/%m/%Y')), company_format)
        sheet.write(4,0, 'Fecha', header_col_format)
        sheet.write(4,1, 'Producto', header_col_format)
        sheet.write(4,2, 'Entradas', header_col_format)
        sheet.write(4,3, 'Salidas', header_col_format)
        sheet.write(4,4, 'Disponibles', header_col_format)
        sheet.write(4,5, 'Lote', header_col_format)
        sheet.write(4,6, 'Días inventario', header_col_format)
        sheet.write(4,7, 'Costo', header_col_format)
        sheet.write(4,8, 'Ingreso del lote', header_col_format)
        sheet.write(4,9, 'Unidad de medida', header_col_format)
        sheet.write(4,10, 'Tipo de movimiento', header_col_format)
        sheet.write(4,11, 'Referencia', header_col_format)
        sheet.write(4,12, 'Doc. de origen', header_col_format)
        sheet.write(4,13, 'Usuario', header_col_format)
        
        
        # busca las lineas que se van a mostrar en el reporte
        
        _logger.info('**** busca los productos porque no estan especificados ')
        move_lines = self.env['stock.move.line'].search([
            ('picking_id.state', '=', 'done'),
            ('lot_id', '!=', False),
            ('date', '<=', report_date_to),
            ('date', '>=', report_date_from)], order='product_id')
            
        _logger.info('**** move_lines: ' + str(move_lines))  

        row = 5
        products = move_lines.mapped('product_id')
        products = list(dict.fromkeys(products))

        for product in products:

            product_row = row
            product_lot_incoming_qtty = 0
            product_lot_outgoing_qtty = 0

            row += 1

            for line in move_lines.filtered(lambda line: line.product_id == product):

                sheet.write(row, 0, str(line.date.strftime('%d/%m/%Y')))
                sheet.write(row, 1, str(line.product_id.name))
                sheet.write(row, 2, str(line.lot_incoming_qtty))
                sheet.write(row, 3, str(line.lot_outgoing_qtty))
                sheet.write(row, 4, str(line.lot_current_stock))
                sheet.write(row, 5, str(line.lot_id.name))
                sheet.write(row, 6, str(line.lot_iddle_time))
                sheet.write(row, 7, str(line.lot_product_cost))
                sheet.write(row, 8, str(line.lot_incoming_date.strftime('%d/%m/%Y') if line.lot_incoming_date else ''))
                sheet.write(row, 9, str(line.product_uom_id.name))
                sheet.write(row, 10, str(line.lot_picking_type.name if line.lot_picking_type else ''))
                sheet.write(row, 11, str(line.reference))
                sheet.write(row, 12, str(line.lot_origin_doc if line.lot_origin_doc else ''))
                sheet.write(row, 13, str(line.lot_uid.name if line.lot_uid.name else ''))
                row += 1

                product_lot_incoming_qtty += line.lot_incoming_qtty
                product_lot_outgoing_qtty += line.lot_outgoing_qtty

            sheet.set_row(product_row, 14)

            sheet.write(product_row, 0, '', header_col_format_gray)
            sheet.write(product_row, 1, str(product.name), header_col_format_gray)
            sheet.write(product_row, 2, str(product_lot_incoming_qtty), header_col_format_gray)
            sheet.write(product_row, 3, str(product_lot_outgoing_qtty), header_col_format_gray)
            sheet.write(product_row, 4, '', header_col_format_gray)
            sheet.write(product_row, 5, '', header_col_format_gray)
            sheet.write(product_row, 6, '', header_col_format_gray)
            sheet.write(product_row, 7, '', header_col_format_gray)
            sheet.write(product_row, 8, '', header_col_format_gray)
            sheet.write(product_row, 9, str(product.uom_id.name), header_col_format_gray)
            sheet.write(product_row, 10, '', header_col_format_gray)
            sheet.write(product_row, 11, '', header_col_format_gray)
            sheet.write(product_row, 12, '', header_col_format_gray)
            sheet.write(product_row, 13, '', header_col_format_gray)

        _logger.info('**** Fin generate_xlsx_report ****')   
