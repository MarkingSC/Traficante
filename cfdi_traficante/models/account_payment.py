# -*- coding: utf-8 -*-

import json
from odoo import fields, models, api,_ , tools
from odoo.tools import float_utils

import pytz
from datetime import datetime
from odoo.exceptions import UserError, Warning
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    folios_cfdi_facturas = fields.Char(string='Folio factura', compute='_get_folios_cfdi_facturas', store=False)
    pue_flag = fields.Boolean(string="Metodo de pago PUE", compute='_compute_pue_flag', store=True)

    def _get_folios_cfdi_facturas(self):
        for payment in self:
            _logger.info('**** entra a _get_folios_cfdi_facturas: ')
            foliosMap = payment.reconciled_invoice_ids.mapped('folio_fiscal')
            foliosStr = [str(folio) for folio in foliosMap if isinstance(folio, str)]
            foliosComa = ','.join(foliosStr)
            payment.folios_cfdi_facturas = foliosComa

    @api.onchange('partner_id')
    def _get_default_forma_pago(self):
        _logger.info('***** Entra a _get_default_forma_pago *****')
        record = self

        if record.partner_id:
            try:
                record.write({'forma_pago': record.partner_id.forma_pago})
                return {record.id:record.partner_id.forma_pago}
            except:
                _logger.info('***** Tiene forma de pago 99, así que se queda vacío *****')
                pass

    def post(self):
        res = super(AccountPayment, self).post()
        for rec in self:
            rec._get_default_forma_pago()
        return res

    forma_pago_2 = fields.Selection(selection=[('01', '01 - Efectivo'), 
                   ('02', '02 - Cheque nominativo'), 
                   ('03', '03 - Transferencia electrónica de fondos'),
                   ('04', '04 - Tarjeta de Crédito'), 
                   ('28', '28 - Tarjeta de débito'), ],
                                string=_('Forma de pago'), default=_get_default_forma_pago
                            )

    methodo_pago = fields.Selection(
        selection=[('PUE', _('Pago en una sola exhibición')),
                   ('PPD', _('Pago en parcialidades o diferido')),],
        string=_('Método de pago'), related='partner_id.methodo_pago'
    )

    @api.onchange('forma_pago_2')
    def _change_forma_pago(self):
        _logger.info('**** entra a _change_forma_pago: ')
        for record in self:
            record.forma_pago = record.forma_pago_2
            _logger.info('**** record.forma_pago: ' + str(record.forma_pago))

    @api.depends('communication')
    def _compute_pue_flag(self):
        for payment in self:
            if payment.communication:
                original_invoice = self.env['account.move'].search([('name', '=', payment.communication)], limit=1)
                payment.pue_flag = original_invoice.methodo_pago == 'PUE' if original_invoice else False
            else:
                payment.pue_flag = False

    # Para enviar de forma automática el complemento de pago una vez timbrado   
    def complete_payment(self):
        _logger.info('**** entra a complete_payment: ')
        if self.pue_flag:
            # Detener el proceso y enviar un mensaje de error
            raise Warning("El método de pago es PUE. No se puede completar el pago.")
        else:
            # Continuar con la ejecución de complete_payment
            _logger.info('**** el usario es  empleado interno: ' + str(self.env.user.has_group('base.group_user')))
            _logger.info('**** el usario es admin: ' + str(self.env.is_admin()))
            _logger.info('**** el usario es el sistema: ' + str(self.env.is_system()))
            result = super(AccountPayment, self).complete_payment()
            # result = super(AccountPayment, self).complete_payment()
            _logger.info('**** Se generó el complemento de pago y se enviará por correo. ')
            self.send_payment()
            # _logger.info('**** Complemento de pago enviado. ')
            return result

    # 23 de Febrero 2022 - Marco Martinez - cambiar el nombre del cliente por la razón social (business_name)
    @api.model
    def to_json(self):
        _logger.info('****** entra a to_json de account_payment ' )
        no_decimales = self.currency_id.no_decimales
        no_decimales_tc = self.currency_id.no_decimales_tc

        self.monedap = self.currency_id.name
        if self.currency_id.name == 'MXN':
            self.tipocambiop = '1'
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
                                    'ImporteP': self.set_decimals(line['ImporteP'],6),
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
        totales.update({'MontoTotalPagos': self.set_decimals(self.amount, 2) if self.monedap == 'MXN' else self.set_decimals(self.amount * float(self.tipocambiop), 2),})
        #totales.update({'MontoTotalPagos': self.set_decimals(self.total_pago, 2),})

        pagos = []
        pagos.append({
                      'FechaPago': date_from,
                      'FormaDePagoP': self.forma_pago,
                      'MonedaP': self.monedap,
                      'TipoCambioP': self.tipocambiop, # if self.monedap != 'MXN' else '1',
                      'Monto':  self.set_decimals(self.amount, no_decimales),
                      #'Monto':  self.set_decimals(self.total_pago/float(self.tipocambiop), no_decimales),
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

        _logger.info('*** json antes de mandar a timbrar: ' + str(request_params))
        return request_params
        
    def set_decimals(self, amount, precision):
        if amount is None or amount is False:
            return None

        if precision > 2:
            return '%.*f' % (precision, amount)
        else:
            return '%.*f' % (precision, float_utils.float_round(amount,precision))

    def add_resitual_amounts(self):
        for payment in self:
          no_decimales = payment.currency_id.no_decimales
          no_decimales_tc = payment.currency_id.no_decimales_tc
          docto_relacionados = []
          tax_grouped_tras = {}
          tax_grouped_ret = {}
          moneda_facturas = payment.invoice_ids.mapped  ('currency_id')[0]
          _logger.info('**** moneda_facturas: ' +  str(moneda_facturas.name))
          factura_extranjera = True if moneda_facturas.name != 'MXN' else False
          if payment.invoice_ids:
            for invoice in payment.invoice_ids:
                if invoice.factura_cfdi:

                    payment_dict = json.loads(invoice.invoice_payments_widget)
                    payment_content = payment_dict['content']
                    monto_pagado = 0                    

                    for invoice_payments in payment_content:

                        _logger.info('**** invoice_payments[amount_mxn] ' +  str(invoice_payments['amount_mxn']))
                        _logger.info('**** invoice_payments: ' +  str(invoice_payments))

                        if invoice_payments['account_payment_id'] == payment.id:
                            monto_pagado = invoice_payments['amount'] if factura_extranjera else invoice_payments['amount_mxn']

                    #revisa la cantidad que se va a pagar en el docuemnto
                    if payment.currency_id.name != invoice.moneda:
                        if payment.currency_id.name == 'MXN':
                            equivalenciadr = round(invoice.currency_id.with_context(date=payment.payment_date).rate,6)
                        else:
                            equivalenciadr = round(float(invoice.tipocambio)/float(payment.currency_id.with_context(date=payment.payment_date).rate),6)
                    else:
                        equivalenciadr = 1

                    decimal_p = 6

                    if not invoice.total_factura > 0:
                       raise Warning("No hay información del monto de la factura. Carga el XML en la factura para agregar el monto total.")

                    paid_pct = payment.truncate(monto_pagado, decimal_p) / invoice.total_factura
                    monto_pagado = payment.truncate(monto_pagado, 2)

                    if not factura_extranjera:
                        if not invoice.tax_payment:
                           raise Warning("No hay información de impuestos en el documento. Carga el XML en la factura para agregar los impuestos.")
                        taxes = json.loads(invoice.tax_payment)
                        objetoimpdr = '01'
                        trasladodr = []
                        retenciondr = []
                        if "translados" in taxes:
                           objetoimpdr = '02'
                           traslados = taxes['translados']
                           for traslado in traslados:
                               basedr = payment.truncate(float(traslado['base']) * paid_pct, decimal_p)
                               importedr = traslado['importe'] and payment.truncate(float(traslado['tasa']) * basedr, decimal_p) or 0
                               trasladodr.append({
                                             'BaseDR': payment.set_decimals(basedr, decimal_p),
                                             'ImpuestoDR': traslado['impuesto'],
                                             'TipoFactorDR': traslado['TipoFactor'],
                                             'TasaOcuotaDR': traslado['tasa'],
                                             'ImporteDR': payment.set_decimals(importedr, decimal_p) if traslado['TipoFactor'] != 'Exento' else '',
                                             })
                               key = traslado['tax_id']

                               basep = basedr / equivalenciadr
                               importep = importedr / equivalenciadr
                               if str(basep)[::-1].find('.') > 6:
                                  basep = payment.truncate(basep, decimal_p)
                               if str(importep)[::-1].find('.') > 6:
                                  importep = payment.truncate(importep, decimal_p)

                               val = {'BaseP': basep,
                                      'ImpuestoP': traslado['impuesto'],
                                      'TipoFactorP': traslado['TipoFactor'],
                                      'TasaOCuotaP': traslado['tasa'],
                                      'ImporteP': importep,}
                               if key not in tax_grouped_tras:
                                   tax_grouped_tras[key] = val
                               else:
                                   tax_grouped_tras[key]['BaseP'] += basep
                                   tax_grouped_tras[key]['ImporteP'] += importep
                        if "retenciones" in taxes:
                           objetoimpdr = '02'
                           retenciones = taxes['retenciones']
                           for retencion in retenciones:
                               basedr = payment.truncate(float(retencion['base']) * paid_pct, decimal_p)
                               importedr = retencion['importe'] and payment.truncate(float(retencion['tasa']) * basedr, decimal_p) or 0
                               retenciondr.append({
                                             'BaseDR': payment.set_decimals(basedr, decimal_p),
                                             'ImpuestoDR': retencion['impuesto'],
                                             'TipoFactorDR': retencion['TipoFactor'],
                                             'TasaOcuotaDR': retencion['tasa'],
                                             'ImporteDR': payment.set_decimals(importedr, decimal_p),
                                             })
                               key = retencion['tax_id']

                               importep = importedr / equivalenciadr
                               if str(importep)[::-1].find('.') > 6:
                                  importep = payment.truncate(importep, decimal_p)

                               val = {'ImpuestoP': retencion['impuesto'],
                                      'ImporteP': importep,}
                               if key not in tax_grouped_ret:
                                   tax_grouped_ret[key] = val
                               else:
                                   tax_grouped_ret[key]['ImporteP'] += importep

                        if objetoimpdr == '02' and not trasladodr and not retenciondr:
                           raise Warning("No hay información de impuestos en el documento. Carga el XML en la factura para agregar los impuestos.")
                    else:
                        objetoimpdr = '01'
                        trasladodr = []
                        retenciondr = []

                    docto_relacionados.append({
                          'MonedaDR': invoice.moneda,
                          'EquivalenciaDR': equivalenciadr,
                          'IdDocumento': invoice.folio_fiscal,
                          'folio_facura': invoice.number_folio,
                          'NumParcialidad': len(payment_content), 
                          'ImpSaldoAnt': payment.set_decimals(invoice.amount_residual + monto_pagado, no_decimales),
                          'ImpPagado': payment.set_decimals(monto_pagado, no_decimales),
                          'ImpSaldoInsoluto': payment.set_decimals(invoice.amount_residual, no_decimales),
                          'ObjetoImpDR': objetoimpdr,
                          'ImpuestosDR': {'traslados': trasladodr, 'retenciones': retenciondr,},
                    })

            payment.write({'docto_relacionados': json.dumps(docto_relacionados), 
                        'retencionesp': json.dumps(tax_grouped_ret), 
                        'trasladosp': json.dumps(tax_grouped_tras),})
