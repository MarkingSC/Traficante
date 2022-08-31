import base64
from email.policy import default
import io
from odoo import models, fields, api, _, exceptions
from datetime import datetime, time, timedelta
import logging

_logger = logging.getLogger(__name__)

class SalesDetailedReport(models.TransientModel):
    _name = 'sales.detailed.report.wizard'

    date_start = fields.Date(string='From date', help='Set the date from you want to get the report.', default = datetime.today().replace(day=1), store = True)
    date_end = fields.Date(string='To date', help='Set the date to you want to get the report.', default = datetime.today(), store = True)

    move_id_state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled')
        ], string='Status', default='posted')

    move_id_estado_factura = fields.Selection(
        selection=[('factura_no_generada', 'Factura no generada'), ('factura_correcta', 'Factura correcta'), 
                   ('solicitud_cancelar', 'Cancelación en proceso'),('factura_cancelada', 'Factura cancelada'),
                   ('solicitud_rechazada', 'Cancelación rechazada')],
        string='Estado de factura', default='factura_correcta')


    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'move_id_state': self.move_id_state,
                'move_id_estado_factura': self.move_id_estado_factura
            },
        }

        return self.env.ref('traficante_sales_detailed_report.action_report_sales_detailed').report_action(self, data=data)

class SalesDetailedReport(models.AbstractModel):
    _name = 'report.sales.detailed.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, goals):
        _logger.info('**** Inicio generate_xlsx_report ****') 

        # Formatea y trunca los filtros de fecha
        date_start = data['form']['date_start'] 
        _logger.info('**** date_start: ' + str(date_start))  
        date_start = datetime.strptime(date_start, '%Y-%m-%d')

        if date_start:
            date_start = date_start
        date_start = datetime.combine(date_start, time.min)

        date_end = data['form']['date_end'] 
        _logger.info('**** date_end: ' + str(date_end))  
        date_end = datetime.strptime(date_end, '%Y-%m-%d')

        if date_end:
            date_end = date_end
        date_end = datetime.combine(date_end, time.max)

        move_id_state = data['form']['move_id_state'] 
        move_id_estado_factura = data['form']['move_id_estado_factura'] 
        
        _logger.info('**** Datos del formulario: ****') 
        _logger.info('**** date_start: ' + str(date_start))
        _logger.info('**** date_end: ' + str(date_end))
        _logger.info('**** move_id_state: ' + str(move_id_state))
        _logger.info('**** move_id_estado_factura: ' + str(move_id_estado_factura))

        # Definición de estilos del excel
        company_format = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bold': True})
        header_col_format = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bold': True, 'bg_color': '#DB3545', 'font_color': 'white'})
        align_center = workbook.add_format({'font_size': 10, 'align': 'vcenter'})
        total_row_format = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bg_color': '#ff585d', 'font_color': 'white'})

        sheet = workbook.add_worksheet('DETALLADO DE VENTAS')
        # sheet.set_column(0, 4, 200)

        # Imprime los encabezados del excel
        if (self.env.user.company_id.logo):
            product_image = io.BytesIO(base64.b64decode(self.env.user.company_id.logo))
            sheet.insert_image(0, 0, "image.png", {'image_data': product_image, 'y_scale': 0.16, 'x_scale': 0.16})
            
        sheet.set_row(0, 120)
        sheet.set_column(0, 2, 20)
        sheet.set_column(3, 3, 50)
        sheet.set_column(5, 6, 15)
        sheet.set_column(7, 12, 20)
        sheet.set_column(13, 18, 50)

        #sheet.insert_image('A1', self.env.user.company_id.logo)
        sheet.merge_range('A2:E2', self.env.company.name, company_format)
        sheet.merge_range('A3:E3', self.env.company.partner_id._display_address(True), company_format)
        sheet.write('A4:B4', self.env.company.vat, company_format)

        sheet.merge_range('A6:M6', 'Detallado de ventas', align_center)
        sheet.merge_range('A7:M7', 'Ventas emitidas del ' + str(date_start.strftime("%d/%m/%Y")) + ' al ' + str(date_end.strftime("%d/%m/%Y")), align_center)

        sheet.write(7,0, 'FACTURA', header_col_format)
        sheet.write(7,1, 'FECHA', header_col_format)
        sheet.write(7,2, 'CODIGO', header_col_format)
        sheet.write(7,3, 'DESCRIPCIÓN', header_col_format)
        sheet.write(7,4, 'CANTIDAD', header_col_format)
        sheet.write(7,5, 'PRECIO', header_col_format)
        sheet.write(7,6, 'SUBTOTAL', header_col_format)
        sheet.write(7,7, 'DESCUENTO', header_col_format)
        sheet.write(7,8, 'IEPS', header_col_format)
        sheet.write(7,9, 'IEPS %', header_col_format)
        sheet.write(7,10, 'IEPS $', header_col_format)
        sheet.write(7,11, 'IVA', header_col_format)
        sheet.write(7,12, 'PRECIO FINAL', header_col_format)
        sheet.write(7,13, 'RAZÓN SOCIAL', header_col_format)
        sheet.write(7,14, 'SUCURSAL / NOMBRE COMERCIAL', header_col_format)
        sheet.write(7,15, 'VENDEDOR', header_col_format)
        sheet.write(7,16, 'RECEPTOR', header_col_format)
        sheet.write(7,17, 'ESTADO DEL DOCUMENTO', header_col_format)
        sheet.write(7,18, 'ESTADO DEL CFDI', header_col_format)
        
        # busca las metas que se van a mostrar en el reporte
        lines = self.env['account.move.line'].search([
            ('display_type', 'not in', ('line_section', 'line_note')),
            ('date', '<=', date_end), 
            ('date', '>=', date_start),
            ('product_id', '!=', False)], order='date,move_id')

        if move_id_state != False:
            lines = lines.filtered(lambda line: line.move_id_state == move_id_state)
        if move_id_estado_factura != False:
            lines = lines.filtered(lambda line: line.move_id_estado_factura == move_id_estado_factura)

        # Variables para Obtención de totales
        total_quantity = 0
        total_price_unit = 0
        total_price_subtotal = 0
        total_ieps_amount = 0
        total_iva_amount = 0
        total_price_total = 0

        row = 9
        for line in lines:
            row = self.print_line_row(row, sheet, line)

            total_quantity += line.quantity
            total_price_unit += line.price_unit
            total_price_subtotal += line.price_subtotal
            total_ieps_amount += line.ieps_amount
            total_iva_amount += line.iva_amount
            total_price_total += line.price_total

        # Impresión de la fila de totales
        sheet.merge_range('A9:D9', 'TOTAL', total_row_format)
        sheet.write(8,4, str("{:,.2f}".format(total_quantity)), total_row_format)
        sheet.write(8,5, str("${:,.2f}".format(total_price_unit)), total_row_format)
        sheet.write(8,6, str("${:,.2f}".format(total_price_subtotal)), total_row_format)
        sheet.write(8,7, '-', total_row_format)
        sheet.write(8,8, '-', total_row_format)
        sheet.write(8,9, '-', total_row_format)
        sheet.write(8,10, str("${:,.2f}".format(total_ieps_amount)), total_row_format)
        sheet.write(8,11, str("${:,.2f}".format(total_iva_amount)), total_row_format)
        sheet.write(8,12, str("${:,.2f}".format(total_price_total)), total_row_format)
        sheet.merge_range('M9:Q9', '', total_row_format)

        _logger.info('**** Fin generate_xlsx_report ****')   

    def print_line_row(self, row, sheet, line):
        _logger.info('**** Inicio print_line_row ****')   
        _logger.info('**** Linea: ' + str(line.name))

        #line.ieps_taxes = line.tax_ids.filtered(lambda tax: tax.tax_group_id.ieps_section == True)
        #line.iva_taxes = line.tax_ids.filtered(lambda tax: tax.tax_group_id.iva_section == True)

        ieps_taxes_str = ','.join(line.ieps_taxes.mapped('name'))

        estado_doc = dict([('draft', 'Draft'),('posted', 'Posted'),('cancel', 'Cancelled')]).get(line.move_id_state)
        estado_cfdi = dict([('factura_no_generada', 'Factura no generada'), ('factura_correcta', 'Factura correcta'), ('solicitud_cancelar', 'Cancelación en proceso'),('factura_cancelada', 'Factura cancelada'),('solicitud_rechazada', 'Cancelación rechazada')]).get(line.move_id_estado_factura)
        _logger.info('**** estado_doc: ' + str(estado_doc))   
        
        sheet.write(row, 0, str(line.move_id.name))
        sheet.write(row, 1, str(line.date))
        sheet.write(row, 2, str(line.product_code))
        sheet.write(row, 3, str(line.product_name))
        sheet.write(row, 4, str(line.quantity))
        sheet.write(row, 5, str("${:,.2f}".format(line.price_unit)))
        sheet.write(row, 6, str("${:,.2f}".format(line.price_subtotal)))
        sheet.write(row, 7, str("{:,.2f}%".format(line.discount)))
        sheet.write(row, 8, str(ieps_taxes_str))
        sheet.write(row, 9, str("{:,.2f}%".format(line.ieps_percent*100)))
        sheet.write(row, 10, str("${:,.2f}".format(line.ieps_amount)))
        sheet.write(row, 11, str("${:,.2f}".format(line.iva_amount)))
        sheet.write(row, 12, str("${:,.2f}".format(line.price_total)))
        sheet.write(row, 13, str(line.business_name))
        sheet.write(row, 14, str(line.commercial_name))
        sheet.write(row, 15, str(line.salesperson))
        sheet.write(row, 16, str(line.partner_id.vat))
        sheet.write(row, 17, str(estado_doc))
        sheet.write(row, 18, str(estado_cfdi))

        row += 1
        _logger.info('**** Fin print_goal_row ****')   
        return row