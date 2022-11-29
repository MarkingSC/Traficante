import base64
from email.policy import default
import io
from odoo import models, fields, api, _, exceptions
from datetime import date, datetime, time, timedelta
import logging

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class StockMarginReportWizard(models.TransientModel):
    _name = 'stock.margin.report.wizard'

    report_on_date = fields.Date(string='To date', help='Set the date until you want to get the report.', default = datetime.today())

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'report_on_date': self.report_on_date
            },
        }

        return self.env.ref('traficante_stock_report.stock_margin_report_xlsx').report_action(self, data=data)


class stockMarginReport(models.AbstractModel):
    _name = 'report.stock.margin.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, products):
        _logger.info('**** Inicio generate_xlsx_report ****') 

        today = date.today()

        # Add a number format for cells with money and color format
        money_format = workbook.add_format(
            {'num_format': '$#,##0.00'})
        
        percent_format = workbook.add_format(
            {'num_format': '#,##0.00%'})
        

        # Definición de estilos del excel
        company_format = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bold': True})
        header_col_format = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bold': True})
        header_col_format_green = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bg_color': '#70bf34', 'bold': True})
        row_format_green = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bg_color': '#70bf34'})

        sheet = workbook.add_worksheet('REVISION ' + today.strftime( '%d%m%y'))
        # sheet.set_column(0, 4, 200)

        # Imprime los encabezados del excel
        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 30)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 16, 20)

        #sheet.insert_image('A1', self.env.user.company_id.logo)
        sheet.merge_range('C3:H3', 'REPORTE DE INVENTARIO CON COSTO Y MARGEN DETALLADO', company_format)
        sheet.write(4,0, 'Código', header_col_format)
        sheet.write(4,1, 'Descripción', header_col_format)
        sheet.write(4,2, 'Grupo', header_col_format)
        sheet.write(4,3, 'Unidad', header_col_format)
        sheet.write(4,4, 'Estatus', header_col_format)
        sheet.write(4,5, 'Último costo', header_col_format)
        sheet.write(4,6, 'Costo Promedio', header_col_format)
        sheet.write(4,7, 'Precio', header_col_format)
        sheet.write(4,8, '% IEPS', header_col_format)
        sheet.write(4,9, '% IVA', header_col_format)
        sheet.write(4,10, 'Precio con IVA', header_col_format)
        sheet.write(4,11, 'Costo con IEPS', header_col_format)
        sheet.write(4,12, 'Costo con impuestos', header_col_format_green)
        sheet.write(4,13, 'Precio con impuestos', header_col_format_green)
        sheet.write(4,14, 'Monto de margen bruto', header_col_format)
        sheet.write(4,15, '% Margen sobre el costo', header_col_format)
        sheet.write(4,16, '% Margen sobre el precio', header_col_format)
        
        if 'form' in data:
            report_on_date = data['form']['report_on_date'] 

            # busca los productos que se van a mostrar en el reporte
            
            _logger.info('**** busca los productos porque no estan especificados ')
            products = self.env['product.template'].search([('standard_price', '!=', False),'|',('active', '=', False),('active', '=', True)], order='name')
            
        else:
            report_on_date = datetime.today()
        
        _logger.info('**** report_on_date: ' + str(report_on_date))  
        _logger.info('**** products: ' + str(products))  

        row = 5
        for product in products:

            latest_active_state = self.env['product.active.history'].search([('product_id', '=', product.id),('date', '<=', report_on_date)], order='date desc', limit=1)

            if latest_active_state:
                _logger.info('**** latest_active_state: ' + str(latest_active_state))  

            # Si no hay un histórico y el producto está activo o si el histórico marca el producto como activo en esa fecha, lo considera en el reporte.
            if (not latest_active_state and product.active) or (latest_active_state and latest_active_state.active_state):
                    
                quantity = 1

                latest_purchase_line = self.env['purchase.order.line'].search([('product_id', '=', product.id), ('date_planned', '<=', report_on_date)], limit = 1, order='date_planned desc')

                latest_product_cost = latest_purchase_line.product_cost
                latest_list_price = latest_purchase_line.list_price
                latest_standard_price = latest_purchase_line.standard_price

                # costo promedio
                latest_avg_cost = 0

                purchase_lines = self.env['purchase.order.line'].search([('product_id', '=', product.id)])
                sum_cost = 0

                for line in purchase_lines:
                    sum_cost += line.price_unit

                if len(purchase_lines) > 0:
                    latest_avg_cost = sum_cost/len(purchase_lines)
                else:
                    latest_avg_cost = 0

                #impuestos

                # Porcentaje de IEPS y ieps_cost
                ieps_taxes = latest_purchase_line.taxes_id.filtered(lambda tax: tax.tax_group_id.ieps_section == True)       

                total_ieps = 0     

                for tax in ieps_taxes:
                        compute_all_res = tax.compute_all(latest_product_cost, product.company_id.currency_id, quantity, product, False, False, handle_price_include=True)

                        for calc_tax in compute_all_res['taxes']:
                            total_ieps += calc_tax['amount']

                ieps_amount = total_ieps

                latest_ieps_tax_pct = 0
                latest_ieps_cost = 0

                if latest_product_cost:
                    latest_ieps_tax_pct = ieps_amount / latest_product_cost
                    latest_ieps_cost = latest_product_cost + ieps_amount

                # Porcentaje de IVA e iva_price
                iva_taxes = product.taxes_id.filtered(lambda tax: tax.tax_group_id.iva_section == True)      
                iva_price = 0      

                if len(iva_taxes) > 1:
                    raise ValidationError(_('Product %s has more than one IVA tax.')%(product.name))
                
                for tax in iva_taxes:
                    computed_iva = tax.compute_all(latest_standard_price, product.company_id.currency_id, quantity, product, False, False, handle_price_include=False)
                    
                    for calc_tax in computed_iva['taxes']:
                        iva_price += calc_tax['amount']

                latest_iva_tax_pct = 0
                latest_iva_price = 0

                if latest_standard_price:
                    latest_iva_tax_pct = iva_price / latest_standard_price
                    latest_iva_price = latest_standard_price + iva_price 

                # Costo con impuestos = Costo con IEPS más IVA
                latest_taxes_cost = latest_ieps_cost * (1+latest_iva_tax_pct)

                # Precio con impuestos = Standard price + IEPS + IVA
                latest_taxes_price = (latest_standard_price * (1+latest_ieps_tax_pct)) * (1+latest_iva_tax_pct)
                

                #márgenes

                latest_total_margin_amt = 0
                latest_cost_margin_pct = 0
                latest_price_margin_pct = 0
                # margen bruto
                latest_total_margin_amt = latest_taxes_price - latest_taxes_cost

                # margen sobre el costo
                if latest_taxes_cost:
                    latest_cost_margin_pct = latest_total_margin_amt / latest_taxes_cost

                # margen sobre el precio
                if latest_taxes_price:
                    latest_price_margin_pct = latest_total_margin_amt / latest_taxes_price 
                

                sheet.write(row, 0, str(product.default_code))
                sheet.write(row, 1, str(product.name))
                sheet.write(row, 2, str(product.categ_id.name))
                sheet.write(row, 3, str(product.uom_id.name))
                sheet.write(row, 4, str('Activo' if product.active else 'Inactivo'))
                sheet.write(row, 5, str(round(latest_product_cost, 2)), money_format)
                sheet.write(row, 6, str(round(latest_avg_cost, 2)), money_format)
                sheet.write(row, 7, str(round(latest_standard_price, 2)), money_format)
                sheet.write(row, 8, str(round((latest_ieps_tax_pct * 100), 2)), percent_format)
                sheet.write(row, 9, str(round((latest_iva_tax_pct * 100), 2)), percent_format)
                sheet.write(row, 10, str(round(latest_iva_price, 2)), money_format)
                sheet.write(row, 11, str(round(latest_ieps_cost, 2)), money_format)
                sheet.write(row, 12, str(round(latest_taxes_cost, 2)), row_format_green)
                sheet.write(row, 13, str(round(latest_taxes_price, 2)), row_format_green)
                sheet.write(row, 14, str(round(latest_total_margin_amt, 2)), money_format)
                sheet.write(row, 15, str(round((latest_cost_margin_pct * 100), 2)), percent_format)
                sheet.write(row, 16, str(round((latest_price_margin_pct * 100), 2)), percent_format)
                row += 1


        _logger.info('**** Fin generate_xlsx_report ****')   
