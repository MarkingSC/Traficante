# -*- coding: utf-8 -*-

import base64
import json
import requests
from odoo import fields, models, api,_ 

import pytz
from datetime import datetime
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

    # 23 de Febrero 2022 - Marco Martinez - cambiar el nombre del cliente por la razón social (business_name)
    @api.model
    def to_json(self):
        _logger.info('****** entra a to_json de account_payment ' )
        no_decimales = self.currency_id.no_decimales
        no_decimales_tc = self.currency_id.no_decimales_tc

        self.monedap = self.currency_id.name
        if self.currency_id.name == 'MXN':
            self.tipocambiop = '1.0'
        else:
            self.tipocambiop = self.set_decimals(1 / self.currency_id.with_context(date=self.payment_date).rate, no_decimales_tc)

        _logger.info('****** self.tipocambiop: ' + self.tipocambiop )

        timezone = self._context.get('tz')
        if not timezone:
            timezone = self.env.user.partner_id.tz or 'America/Mexico_City'
        #timezone = tools.ustr(timezone).encode('utf-8')

        if not self.fecha_pago:
            raise Warning("Falta configurar fecha de pago en la sección de CFDI del documento.")
        else:
            local = pytz.timezone(timezone)
            naive_from = self.fecha_pago
            local_dt_from = naive_from.replace(tzinfo=pytz.UTC).astimezone(local)
            date_from = local_dt_from.strftime ("%Y-%m-%dT%H:%M:%S")
        self.add_resitual_amounts()

        #corregir hora
        local2 = pytz.timezone(timezone)
        naive_from2 = datetime.now() 
        local_dt_from2 = naive_from2.replace(tzinfo=pytz.UTC).astimezone(local2)
        date_payment = local_dt_from2.strftime ("%Y-%m-%dT%H:%M:%S")

        self.check_cfdi_values()

        if self.partner_id.vat == 'XAXX010101000':
            nombre = 'PUBLICO GENERAL'
        else:
            nombre = self.partner_id.business_name.upper()

        conceptos = []
        conceptos.append({
                          'ClaveProdServ': '84111506',
                          'ClaveUnidad': 'ACT',
                          'cantidad': 1,
                          'descripcion': 'Pago',
                          'valorunitario': '0',
                          'importe': '0',
                          'ObjetoImp': '01',
                    })

        taxes_traslado = json.loads(self.trasladosp)
        taxes_retenciones = json.loads(self.retencionesp)
        impuestosp = {}
        totales = {}
        self.total_pago = 0
        if taxes_traslado or taxes_retenciones:
           retencionp = []
           trasladop = []
           if taxes_traslado:
              for line in taxes_traslado.values():
                  trasladop.append({'ImpuestoP': line['ImpuestoP'],
                                    'TipoFactorP': line['TipoFactorP'],
                                    'TasaOCuotaP': line['TasaOCuotaP'],
                                    'ImporteP': self.set_decimals(line['ImporteP'],6) if line['TipoFactorP'] != 'Exento' else '',
                                    'BaseP': self.set_decimals(line['BaseP'],6),
                                    })
                  if line['ImpuestoP'] == '002' and line['TasaOCuotaP'] == '0.160000':
                       totales.update({'TotalTrasladosBaseIVA16': self.set_decimals(line['BaseP'] * float(self.tipocambiop),2),
                                       'TotalTrasladosImpuestoIVA16': self.set_decimals(line['ImporteP'] * float(self.tipocambiop),2),})
                  if line['ImpuestoP'] == '002' and line['TasaOCuotaP'] == '0.080000':
                       totales.update({'TotalTrasladosBaseIVA8': self.set_decimals(line['BaseP'] * float(self.tipocambiop),2),
                                       'TotalTrasladosImpuestoIVA8': self.set_decimals(line['ImporteP'] * float(self.tipocambiop),2),})
                  if line['ImpuestoP'] == '002' and line['TasaOCuotaP'] == '0.000000':
                       totales.update({'TotalTrasladosBaseIVA0': self.set_decimals(line['BaseP'] * float(self.tipocambiop),2),
                                       'TotalTrasladosImpuestoIVA0': self.set_decimals(line['ImporteP'] * float(self.tipocambiop),2),})
                  if line['ImpuestoP'] == '002' and line['TipoFactorP'] == 'Exento':
                       totales.update({'TotalTrasladosBaseIVAExento': self.set_decimals(line['BaseP'] * float(self.tipocambiop),2),})
                  if line['TipoFactorP'] != 'Exento':
                     self.total_pago += round(line['BaseP'] * float(self.tipocambiop),2) + round(line['ImporteP'] * float(self.tipocambiop),2)
                  else:
                     self.total_pago += round(line['BaseP'] * float(self.tipocambiop),2)
              impuestosp.update({'TrasladosP': trasladop})
           if taxes_retenciones:
              for line in taxes_retenciones.values():
                  retencionp.append({'ImpuestoP': line['ImpuestoP'],
                                    'ImporteP': self.set_decimals(line['ImporteP'],no_decimales),
                                    })
                  if line['ImpuestoP'] == '002':
                       totales.update({'TotalRetencionesIVA': self.set_decimals(line['ImporteP'],2),})
                  if line['ImpuestoP'] == '001':
                       totales.update({'TotalRetencionesISR': self.set_decimals(line['ImporteP'],2),})
                  if line['ImpuestoP'] == '003':
                       totales.update({'TotalRetencionesIEPS': self.set_decimals(line['ImporteP'],2),})
                  self.total_pago -= round(line['ImporteP'] * float(self.tipocambiop),2)
                  #self.total_pago -= round(line['BaseP'] * float(self.tipocambiop),2) + round(line['ImporteP'] * float(self.tipocambiop),2)
              impuestosp.update({'RetencionesP': retencionp})
        totales.update({'MontoTotalPagos': self.set_decimals(self.total_pago, 2),})

        pagos = []
        pagos.append({
                      'FechaPago': date_from,
                      'FormaDePagoP': self.forma_pago,
                      'MonedaP': self.monedap,
                      'TipoCambioP': self.tipocambiop if self.monedap != 'MXN' else '1',
                      'Monto':  self.set_decimals(self.total_pago/float(self.tipocambiop), no_decimales),
#                      'Monto':  self.set_decimals(self.total_pago, no_decimales) if self.monedap == 'MXN' else self.set_decimals(self.total_pago/float(self.tipocambiop), no_decimales),
                      'NumOperacion': self.numero_operacion,

                      'RfcEmisorCtaOrd': self.rfc_banco_emisor if self.forma_pago in ['02', '03', '04', '05', '28', '29'] else '',
                      'NomBancoOrdExt': self.banco_emisor if self.forma_pago in ['02', '03', '04', '05', '28', '29'] else '',
                      'CtaOrdenante': self.cuenta_emisor.acc_number if self.cuenta_emisor and self.forma_pago in ['02', '03', '04', '05', '28', '29'] else '',
                      'RfcEmisorCtaBen': self.rfc_banco_receptor if self.forma_pago in ['02', '03', '04', '05', '28', '29'] else '',
                      'CtaBeneficiario': self.cuenta_beneficiario if self.forma_pago in ['02', '03', '04', '05', '28', '29'] else '',
                      'DoctoRelacionado': json.loads(self.docto_relacionados),
                      'ImpuestosP': impuestosp,
                    })

        if self.reconciled_invoice_ids:
            request_params = {
                'factura': {
                      'serie': self.company_id.serie_complemento,
                      'folio': self.name.replace('CUST.IN','').replace('/',''),
                      'fecha_expedicion': date_payment,
                      'subtotal': '0',
                      'moneda': 'XXX',
                      'total': '0',
                      'tipocomprobante': 'P',
                      'LugarExpedicion': self.journal_id.codigo_postal or self.company_id.zip,
                      'confirmacion': self.confirmacion,
                      'Exportacion': '01',
                },
                'emisor': {
                      'rfc': self.company_id.vat.upper(),
                      'nombre': self.company_id.nombre_fiscal.upper(),
                      'RegimenFiscal': self.company_id.regimen_fiscal,
                },
                'receptor': {
                      'nombre': nombre,
                      'rfc': self.partner_id.vat.upper(),
                      'ResidenciaFiscal': self.partner_id.residencia_fiscal,
                      'NumRegIdTrib': self.partner_id.registro_tributario,
                      'UsoCFDI': 'CP01',
                      'RegimenFiscalReceptor': self.partner_id.regimen_fiscal,
                      'DomicilioFiscalReceptor': self.partner_id.zip,
                },

                'informacion': {
                      'cfdi': '4.0',
                      'sistema': 'odoo13',
                      'version': '6',
                      'api_key': self.company_id.proveedor_timbrado,
                      'modo_prueba': self.company_id.modo_prueba,
                },

                'conceptos': conceptos,

                'totales': totales,

                'pagos20': {'Pagos': pagos},

            }

            if self.uuid_relacionado:
              cfdi_relacionado = []
              uuids = self.uuid_relacionado.replace(' ','').split(',')
              for uuid in uuids:
                   cfdi_relacionado.append({
                         'uuid': uuid,
                   })
              request_params.update({'CfdisRelacionados': {'UUID': cfdi_relacionado, 'TipoRelacion':self.tipo_relacion }})

        else:
            raise Warning("No tiene ninguna factura ligada al documento de pago, debe al menos tener una factura ligada. \n Desde la factura crea el pago para que se asocie la factura al pago.")
        return request_params
