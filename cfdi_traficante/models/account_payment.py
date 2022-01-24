# -*- coding: utf-8 -*-

import base64
import json
import requests
from odoo import fields, models, api,_ 
from odoo.exceptions import UserError, Warning
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Para enviar de forma automática el complemento de pago una vez timbrado   
    def complete_payment(self):
        _logger.info('**** entra a complete_payment: ')
        result = super(AccountPayment, self).complete_payment()
        _logger.info('**** Se generó el complemento de pago y se enviará por correo. ')
        self.send_payment()
        _logger.info('**** Complemento de pago enviado. ')
        return result

    # Para enciar de forma automática la cancelación del complemento de pago una vez cancelado
    #def action_cfdi_cancel(self):
    #    _logger.info('**** entra a action_cfdi_cancel: ')
    #    result = super(AccountPayment, self).action_cfdi_cancel()
    #    _logger.info('**** Se candeló el complemento de pago y se enviará por correo. ')
    #    self.send_payment()
    #    _logger.info('**** Complemento de pago cancelado y enviado. ')
    #    return result

    # Corrección de la función para poder cancelar, se comenta la sección donde dice datas_fname - 23 enero 2022 @marking
    def action_cfdi_cancel(self):
        _logger.info('**** entra a action_cfdi_cancel: ')
        for p in self:
            #if invoice.factura_cfdi:
                if p.estado_pago == 'factura_cancelada':
                    pass
                    # raise UserError(_('La factura ya fue cancelada, no puede volver a cancelarse.'))
                if not p.company_id.archivo_cer:
                    raise UserError(_('Falta la ruta del archivo .cer'))
                if not p.company_id.archivo_key:
                    raise UserError(_('Falta la ruta del archivo .key'))
                archivo_cer = p.company_id.archivo_cer.decode("utf-8")
                archivo_key = p.company_id.archivo_key.decode("utf-8")
                archivo_xml_link = p.company_id.factura_dir + '/' + p.name.replace('/', '_') + '.xml'
                with open(archivo_xml_link, 'rb') as cf:
                    archivo_xml = base64.b64encode(cf.read())
                values = {
                          'rfc': p.company_id.rfc,
                          'api_key': p.company_id.proveedor_timbrado,
                          'uuid': p.folio_fiscal,
                          'folio': p.folio,
                          'serie_factura': p.company_id.serie_complemento,
                          'modo_prueba': p.company_id.modo_prueba,
                            'certificados': {
                                  'archivo_cer': archivo_cer,
                                  'archivo_key': archivo_key,
                                  'contrasena': p.company_id.contrasena,
                            },
                          'xml': archivo_xml.decode("utf-8"),
                          }
                if p.company_id.proveedor_timbrado == 'multifactura':
                    url = '%s' % ('http://facturacion.itadmin.com.mx/api/refund')
                elif p.company_id.proveedor_timbrado == 'multifactura2':
                    url = '%s' % ('http://facturacion2.itadmin.com.mx/api/refund')
                elif p.company_id.proveedor_timbrado == 'multifactura3':
                    url = '%s' % ('http://facturacion3.itadmin.com.mx/api/refund')
                elif p.company_id.proveedor_timbrado == 'gecoerp':
                    if p.company_id.modo_prueba:
                        #url = '%s' % ('https://ws.gecoerp.com/itadmin/pruebas/refund/?handler=OdooHandler33')
                        url = '%s' % ('https://itadmin.gecoerp.com/refund/?handler=OdooHandler33')
                    else:
                        url = '%s' % ('https://itadmin.gecoerp.com/refund/?handler=OdooHandler33')
                response = requests.post(url , 
                                         auth=None,verify=False, data=json.dumps(values), 
                                         headers={"Content-type": "application/json"})

                json_response = response.json()
                
                if json_response['estado_factura'] == 'problemas_factura':
                    raise UserError(_(json_response['problemas_message']))
                elif json_response.get('factura_xml', False):
                    if p.name:
                        xml_file_link = p.company_id.factura_dir + '/CANCEL_' + p.name.replace('/', '_') + '.xml'
                    else:
                        xml_file_link = p.company_id.factura_dir + '/CANCEL_' + p.folio + '.xml'
                    xml_file = open(xml_file_link, 'w')
                    xml_invoice = base64.b64decode(json_response['factura_xml'])
                    xml_file.write(xml_invoice.decode("utf-8"))
                    xml_file.close()
                    if p.name:
                        file_name = p.name.replace('/', '_') + '.xml'
                    else:
                        file_name = p.folio + '.xml'
                    self.env['ir.attachment'].sudo().create(
                                                {
                                                    'name': file_name,
                                                    'datas': json_response['factura_xml'],
                                                    #'datas_fname': file_name,
                                                    'res_model': self._name,
                                                    'res_id': p.id,
                                                    'type': 'binary'
                                                })
                p.write({'estado_pago': json_response['estado_factura']})
                p.message_post(body="CFDI Cancelado")
                # Se manda por correo  - 23 Enero 2022 @marking
                self.send_payment()

