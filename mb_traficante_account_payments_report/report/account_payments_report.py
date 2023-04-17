import base64
from email.policy import default
import io
from odoo import models, fields, api, _, exceptions
from datetime import datetime, time, timedelta
import logging

_logger = logging.getLogger(__name__)

class AccountPaymentsReport(models.TransientModel):
    _name = 'account.payments.report.wizard'

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
        
    partner_id = fields.Many2one('res.partner', string='Partner')


    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'move_id_state': self.move_id_state,
                'move_id_estado_factura': self.move_id_estado_factura,
                'partner_id': self.partner_id.id
            },
        }

        return self.env.ref('mb_traficante_account_payments_report.action_account_payments_report').report_action(self, data=data)

class AccountPaymentsReport(models.AbstractModel):
    _name = 'report.account.payments.report'
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
        move_id_partner_id = data['form']['partner_id']
        
        _logger.info('**** Datos del formulario: ****') 
        _logger.info('**** date_start: ' + str(date_start))
        _logger.info('**** date_end: ' + str(date_end))
        _logger.info('**** move_id_state: ' + str(move_id_state))
        _logger.info('**** move_id_partner_id: ' + str(move_id_partner_id))
        _logger.info('**** move_id_estado_factura: ' + str(move_id_estado_factura))

        # Definición de estilos del excel
        super_header_col_format = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'align': 'center', 'bold': True, 'border': 2})
        header_col_format = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'align': 'center', 'bold': True, 'bg_color': '#e0e0e0', 'font_color': 'black', 'border': 1})
        align_center = workbook.add_format({'font_size': 10, 'align': 'vcenter'})
        total_row_format = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bg_color': '#ff585d', 'font_color': 'white'})

        sheet = workbook.add_worksheet('CONTABILIDAD Y COBRANZA')
        # sheet.set_column(0, 4, 200)

        '''
        sheet.set_row(0, 120)
        sheet.set_column(0, 2, 20)
        sheet.set_column(3, 3, 50)
        sheet.set_column(5, 6, 15)
        sheet.set_column(7, 12, 20)
        sheet.set_column(13, 18, 50)
        '''

        #sheet.insert_image('A1', self.env.user.company_id.logo)
        sheet.merge_range('A1:K1', 'FACTURA', super_header_col_format)
        sheet.merge_range('L1:N1', 'PAGO', super_header_col_format)
        sheet.merge_range('O1:Q1', 'PARCIALIDAD 1', super_header_col_format)
        sheet.merge_range('R1:T1', 'PARCIALIDAD 2', super_header_col_format)
        sheet.merge_range('U1:W1', 'PARCIALIDAD 3', super_header_col_format)
        sheet.merge_range('X1:Z1', 'PARCIALIDAD 4', super_header_col_format)
        sheet.merge_range('AA1:AC1', 'INFORMATIVA', super_header_col_format)

        sheet.write(1,0, 'ESTATUS UUID', header_col_format)
        sheet.write(1,1, 'SERIE', header_col_format)
        sheet.write(1,2, 'FOLIO', header_col_format)
        sheet.write(1,3, 'EMISIÓN', header_col_format)
        sheet.write(1,4, 'RECEPTOR', header_col_format)
        sheet.write(1,5, 'SUBTOTAL', header_col_format)
        sheet.write(1,6, 'DESCUENTO', header_col_format)
        sheet.write(1,7, 'IVA', header_col_format)
        sheet.write(1,8, 'MTO. IEPS', header_col_format)
        sheet.write(1,9, 'IEPS', header_col_format)
        sheet.write(1,10, 'TOTAL', header_col_format)
        sheet.write(1,11, 'IMP.PAGADO', header_col_format)
        sheet.write(1,12, 'RESTANTE', header_col_format)
        sheet.write(1,13, 'FECHA DE PAGO', header_col_format)
        sheet.write(1,14, 'FECHA DE PAGO', header_col_format)
        sheet.write(1,15, 'CONCEPTO DE PAGO', header_col_format)
        sheet.write(1,16, 'REP', header_col_format)
        sheet.write(1,17, 'FECHA DE PAGO', header_col_format)
        sheet.write(1,18, 'CONCEPTO DE PAGO', header_col_format)
        sheet.write(1,19, 'REP', header_col_format)
        sheet.write(1,20, 'FECHA DE PAGO', header_col_format)
        sheet.write(1,21, 'CONCEPTO DE PAGO', header_col_format)
        sheet.write(1,22, 'REP', header_col_format)
        sheet.write(1,23, 'FECHA DE PAGO', header_col_format)
        sheet.write(1,24, 'CONCEPTO DE PAGO', header_col_format)
        sheet.write(1,25, 'REP', header_col_format)
        sheet.write(1,26, 'NOTA DE CRÉDITO', header_col_format)
        sheet.write(1,27, 'FOLIO DE SUSTITUCIÓN', header_col_format)
        sheet.write(1,28, 'MTO. DE SUSTITUCIÓN', header_col_format)
        
        # busca las facturas que se van a mostrar en el reporte
        moves = self.env['account.move'].search([
            ('date', '<=', date_end), 
            ('date', '>=', date_start)], order='date,id')

        if move_id_state != False:
            moves = moves.filtered(lambda line: line.state == move_id_state)
        if move_id_estado_factura != False:
            moves = moves.filtered(lambda line: line.estado_factura == move_id_estado_factura)
        if move_id_partner_id != False:
            moves = moves.filtered(lambda line: line.partner_id == move_id_partner_id)

        '''
        # Variables para Obtención de totales
        total_quantity = 0
        total_price_unit = 0
        total_price_subtotal = 0
        total_ieps_amount = 0
        total_iva_amount = 0
        total_price_total = 0
        '''

        row = 2
        for move in moves:
            row = self.print_line_row(row, sheet, move)

            '''
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
        '''

        _logger.info('**** Fin generate_xlsx_report ****')   

    def print_line_row(self, row, sheet, move):
        _logger.info('**** Inicio print_line_row ****')   
        _logger.info('**** Linea: ' + str(move.name))

        #line.ieps_taxes = line.tax_ids.filtered(lambda tax: tax.tax_group_id.ieps_section == True)
        #line.iva_taxes = line.tax_ids.filtered(lambda tax: tax.tax_group_id.iva_section == True)

        estado_factura_dict = {'factura_no_generada': 'Factura no generada', 'factura_correcta': 'Factura correcta', 'solicitud_cancelar': 'Cancelación en proceso', 'factura_cancelada': 'Factura cancelada','solicitud_rechazada': 'Cancelación rechazada'}

        ieps_taxes_str = ','.join(move.ieps_taxes.mapped('name'))

        estado_doc = dict([('draft', 'Draft'),('posted', 'Posted'),('cancel', 'Cancelled')]).get(move.state)
        estado_cfdi = dict([('factura_no_generada', 'Factura no generada'), ('factura_correcta', 'Factura correcta'), ('solicitud_cancelar', 'Cancelación en proceso'),('factura_cancelada', 'Factura cancelada'),('solicitud_rechazada', 'Cancelación rechazada')]).get(move.estado_factura)
        _logger.info('**** estado_doc: ' + str(estado_doc))   
        
        #FACTURA
        sheet.write(row, 0, str(estado_factura_dict[move.estado_factura]))
        sheet.write(row, 1, str(move.company_id.serie_factura))
        sheet.write(row, 2, str(move.folio_fiscal))
        sheet.write(row, 3, str(move.date))
        sheet.write(row, 4, str(move.partner_id.name))
        sheet.write(row, 5, str("${:,.2f}".format(move.amount_untaxed)))
        sheet.write(row, 6, str("${:,.2f}".format(move.discount)))
        sheet.write(row, 7, str("${:,.2f}".format(move.iva_amount)))
        sheet.write(row, 8, str("${:,.2f}".format(move.ieps_amount)))
        sheet.write(row, 9, str(ieps_taxes_str))
        sheet.write(row, 10, str("${:,.2f}".format(move.amount_total)))

        #Busca los documentos de pago relacionados
        payments = self.env['account.payment'].search([('state', 'in', ['posted','sent','reconciled'])]).filtered(lambda payment: move in payment.invoice_ids)
        payments = payments.sorted(key=lambda r: r.payment_date)
        payments = payments

        _logger.info('payments: '+ str(payments))
        _logger.info('len(payments): '+ str(len(payments)))

        imp_pagado = 0
        fecha_pago = False

        max_range = len(payments) if len(payments) < 5 else 4
        _logger.info('max_range: '+ str(max_range))
        for i in range(max_range):
            imp_pagado += payments[i].amount
            if i == max_range-1:
                fecha_pago = payments[i].payment_date
        
        imp_restante = move.amount_total - imp_pagado

        # PAGO
        sheet.write(row, 11, str("${:,.2f}".format(imp_pagado)))
        sheet.write(row, 12, str("${:,.2f}".format(imp_restante)))
        sheet.write(row, 13, str(fecha_pago.strftime('%d/%m/%Y') if fecha_pago else ''))        

        # PLAZOS
        # Imprime las columnas para los datos de plazos de pago.
        if max_range > 0:
            sheet.write(row, 14, str(payments[0].payment_date.strftime('%d/%m/%Y')))
            sheet.write(row, 15, str(payments[0].bank_reference if payments[0].bank_reference else ''))
            sheet.write(row, 16, str(payments[0].folio_fiscal if payments[0].folio_fiscal else ''))
        if max_range > 1:
            sheet.write(row, 17, str(payments[1].payment_date.strftime('%d/%m/%Y')))
            sheet.write(row, 18, str(payments[1].bank_reference if payments[1].bank_reference else ''))
            sheet.write(row, 19, str(payments[1].folio_fiscal if payments[1].folio_fiscal else ''))
        if max_range > 2:
            sheet.write(row, 20, str(payments[2].payment_date.strftime('%d/%m/%Y')))
            sheet.write(row, 21, str(payments[2].bank_reference if payments[2].bank_reference else ''))
            sheet.write(row, 22, str(payments[2].folio_fiscal if payments[2].folio_fiscal else ''))
        if max_range > 3:
            sheet.write(row, 23, str(payments[3].payment_date.strftime('%d/%m/%Y')))
            sheet.write(row, 24, str(payments[3].bank_reference if payments[3].bank_reference else ''))
            sheet.write(row, 25, str(payments[3].folio_fiscal if payments[3].folio_fiscal else ''))

        # INFORMATIVA

        # OBTENER NOTA DE CRÉDITO ASOCIADA
        nc_asociada = move.reversal_move_id.filtered(lambda nc: nc.state == 'posted')
        nc_asociada = nc_asociada[0] if len(nc_asociada) > 0 else False

        # OBTENER EL FOLIO DE LA FACTURA QUE LA SUSTITUYE

        susticion = False
        if move.folio_fiscal:
            sustitucion = self.env['account.move'].search([('uuid_relacionado', '=', move.folio_fiscal), ('state', 'in', ['posted','sent','reconciled']), ('tipo_comprobante', '=', 'I')], limit=1)

        # OBTENER EL MONTO DE LA FACTURA QUE LA SUSTITUYE
        mto_sustitucion = 0

        sheet.write(row, 26, str("${:,.2f}".format(nc_asociada.amount_total) if nc_asociada else ''))
        sheet.write(row, 27, str(sustitucion.folio_fiscal if sustitucion else ''))
        sheet.write(row, 28, str("${:,.2f}".format(sustitucion.amount_total) if susticion else ''))
        
        row += 1
        _logger.info('**** Fin print_goal_row ****')   
        
        return row