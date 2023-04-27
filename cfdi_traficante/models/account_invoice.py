# -*- coding: utf-8 -*-

from odoo import fields, models, api,_, tools
from odoo.tools import float_utils

import pytz
import datetime
from odoo.exceptions import UserError, Warning
from odoo.tools import date_utils, float_is_zero
import json

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    forma_pago = fields.Selection(
        selection=[('01', '01 - Efectivo'), 
                   ('02', '02 - Cheque nominativo'), 
                   ('03', '03 - Transferencia electrónica de fondos'),
                   ('04', '04 - Tarjeta de Crédito'), 
                   ('05', '05 - Monedero electrónico'),
                   ('06', '06 - Dinero electrónico'), 
                   ('08', '08 - Vales de despensa'), 
                   ('12', '12 - Dación en pago'), 
                   ('13', '13 - Pago por subrogación'), 
                   ('14', '14 - Pago por consignación'), 
                   ('15', '15 - Condonación'), 
                   ('17', '17 - Compensación'), 
                   ('23', '23 - Novación'), 
                   ('24', '24 - Confusión'), 
                   ('25', '25 - Remisión de deuda'), 
                   ('26', '26 - Prescripción o caducidad'), 
                   ('27', '27 - A satisfacción del acreedor'), 
                   ('28', '28 - Tarjeta de débito'), 
                   ('29', '29 - Tarjeta de servicios'), 
                   ('30', '30 - Aplicación de anticipos'), 
                   ('99', '99 - Por definir'),],
        string=_('Forma de pago'), required = True
    )
    methodo_pago = fields.Selection(
        selection=[('PUE', _('Pago en una sola exhibición')),
				   ('PPD', _('Pago en parcialidades o diferido')),],
        string=_('Método de pago'), required = True
    )
    uso_cfdi = fields.Selection(
        selection=[('G01', _('Adquisición de mercancías')),
                   ('G02', _('Devoluciones, descuentos o bonificaciones')),
                   ('G03', _('Gastos en general')),
                   ('I01', _('Construcciones')),
                   ('I02', _('Mobiliario y equipo de oficina por inversiones')),
                   ('I03', _('Equipo de transporte')),
                   ('I04', _('Equipo de cómputo y accesorios')),
                   ('I05', _('Dados, troqueles, moldes, matrices y herramental')),
                   ('I06', _('Comunicacion telefónica')),
                   ('I07', _('Comunicación Satelital')),
                   ('I08', _('Otra maquinaria y equipo')),
                   ('D01', _('Honorarios médicos, dentales y gastos hospitalarios')),
                   ('D02', _('Gastos médicos por incapacidad o discapacidad')),
                   ('D03', _('Gastos funerales')),
                   ('D04', _('Donativos')),
                   ('D05', _('Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación).')),
                   ('D06', _('Aportaciones voluntarias al SAR.')),
                   ('D07', _('Primas por seguros de gastos médicos')),
                   ('D08', _('Gastos de transportación escolar obligatoria')),
                   ('D09', _('Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones')),
                   ('D10', _('Pagos por servicios educativos (colegiaturas)')),
                   ('S01', _('Sin efectos fiscales')),
                   ('P01', _('Por definir (obsoleto)')),],
        string=_('Uso CFDI (cliente)'), required = True
    )

    motivo_cancelacion = fields.Selection(
        selection=[('01', ('Comprobante emitido con errores con relación')),
                   ('02', ('Comprobante emitido con errores sin relación')),
                   ('03', ('No se llevó a cabo la operación')),
                   ('04', ('Operación nominativa relacionada en la factura global')),
                   ],
        string=('Motivo de cancelación'), 
    )


    @api.onchange("partner_id")
    def get_cfdi_data_from_partner(self):
        self.methodo_pago = self.partner_id.methodo_pago
        self.forma_pago = self.partner_id.forma_pago
        self.uso_cfdi = self.partner_id.uso_cfdi

    # Envía de forma automática el correo de la factura cuando se timbre
    def action_cfdi_generate(self):
        _logger.info('**** entra a action_cfdi_generate: ')
        for invoice in self:
            invoice.write({'proceso_timbrado': False})
            #self.env.cr.commit()
        result = super(AccountMove, self).action_cfdi_generate()
        _logger.info('**** result de action_cfdi_generate: ' + str(result))
        #if result == True:
            #_logger.info('**** Se generó el CFDI y se enviará por correo. ')
            #self.force_invoice_send()
            #_logger.info('**** Factura enviada. ')
        return result

    # Pinta en el log los parámetros a envair para un CFDI
    @api.model
    def to_json(self):
        result = super(AccountMove, self).to_json()
        _logger.info('**** JSON que se envía a timbrar: ' + str(result))

    # Envía de forma automática el correo de la Nota de crédito cuando se timbre
    def action_cfdi_cancel(self):
        _logger.info('***** entra a action_cfdi_cancel *****')
        result = super(AccountMove, self).action_cfdi_cancel()
        #_logger.info('**** Se generó la nota de credito y se enviará por correo. ')
        #self.force_invoice_send() en realidad la cancelación del cfdi no es como tal la creacion de la nota de crédito
        #_logger.info('**** Nota de crédito enviada. ')

    @api.model
    def _reverse_move_vals(self,default_values, cancel=True):
    # Cuando se crea una nota de crédito la crea desde 0 para que se pueda timbrar
        values = super(AccountMove, self)._reverse_move_vals(default_values, cancel)
        if self.estado_factura == 'factura_correcta':
            values['estado_factura'] = 'factura_no_generada'
            values['folio_fiscal'] = ''
            values['fecha_factura'] = None
            values['factura_cfdi'] = False
        return values

    @api.model
    def to_json(self):
        if self.partner_id.vat == 'XAXX010101000' and self.factura_global:
            nombre = 'PUBLICO EN GENERAL'
        else:
            nombre = self.partner_id.business_name.upper()

        no_decimales = self.currency_id.no_decimales
        no_decimales_prod = self.currency_id.decimal_places
        no_decimales_tc = self.currency_id.no_decimales_tc
        factura_extranjera = True if self.currency_id.name != 'MXN' else False

        #corregir hora
        timezone = self._context.get('tz')
        if not timezone:
            timezone = self.journal_id.tz or self.env.user.partner_id.tz or 'America/Mexico_City'
        #timezone = tools.ustr(timezone).encode('utf-8')

        local = pytz.timezone(timezone)
        if not self.fecha_factura:
           naive_from = datetime.datetime.now()
        else:
           naive_from = self.fecha_factura
        local_dt_from = naive_from.replace(tzinfo=pytz.UTC).astimezone(local)
        date_from = local_dt_from.strftime ("%Y-%m-%dT%H:%M:%S")
        if not self.fecha_factura:
           self.fecha_factura = datetime.datetime.now()

        if self.currency_id.name == 'MXN':
           tipocambio = 1
        else:
           #tipocambio = self.set_decimals(1 / self.currency_id.with_context(date=self.invoice_date).rate, no_decimales_tc)
           tipocambio = self.set_decimals(self.currency_rate, no_decimales_tc)

        self.check_cfdi_values()

        request_params = {
                'factura': {
                      'serie': self.journal_id.serie_diario or self.company_id.serie_factura,
                      'folio': self.name.replace('INV','').replace('/',''),
                      'fecha_expedicion': date_from,
                      'forma_pago': self.forma_pago,
                      'subtotal': self.amount_untaxed,
                      'descuento': 0,
                      'moneda': self.currency_id.name,
                      'tipocambio': tipocambio,
                      'total': self.amount_total,
                      'tipocomprobante': self.tipo_comprobante,
                      'metodo_pago': self.methodo_pago,
                      'LugarExpedicion': self.journal_id.codigo_postal or self.company_id.zip,
                      'Confirmacion': self.confirmacion,
                      'Exportacion': self.exportacion,
                },
                'emisor': {
                      'rfc': self.company_id.vat.upper(),
                      'nombre': self.company_id.nombre_fiscal.upper(),
                      'RegimenFiscal': self.company_id.regimen_fiscal,
                      'FacAtrAdquirente': self.facatradquirente,
                },
                'receptor': {
                      'nombre': nombre,
                      'rfc': self.partner_id.vat.upper(),
                      'ResidenciaFiscal': self.partner_id.residencia_fiscal,
                      'NumRegIdTrib': self.partner_id.registro_tributario,
                      'UsoCFDI': self.uso_cfdi,
                      'RegimenFiscalReceptor': self.partner_id.regimen_fiscal,
                      'DomicilioFiscalReceptor': self.partner_id.zip,
                },
                'informacion': {
                      'cfdi': '4.0',
                      'sistema': 'odoo13',
                      'version': '1',
                      'api_key': self.company_id.proveedor_timbrado,
                      'modo_prueba': self.company_id.modo_prueba,
                },
        }

        if self.factura_global:
           request_params.update({
                'InformacionGlobal': {
                      'Periodicidad': self.fg_periodicidad,
                      'Meses': self.fg_meses,
                      'Año': self.fg_ano,
                },
           })

        if self.uuid_relacionado:
           cfdi_relacionado = []
           uuids = self.uuid_relacionado.replace(' ','').split(',')
           for uuid in uuids:
                cfdi_relacionado.append({
                      'uuid': uuid,
                })
           request_params.update({'CfdisRelacionados': {'UUID': cfdi_relacionado, 'TipoRelacion':self.tipo_relacion }})

        amount_total = 0.0
        amount_untaxed = 0.0
        self.subtotal = 0
        total = 0
        self.discount = 0
        tras_tot = 0
        ret_tot = 0
        tax_grouped_tras = {}
        tax_grouped_ret = {}
        tax_local_ret = []
        tax_local_tras = []
        tax_local_ret_tot = 0
        tax_local_tras_tot = 0
        items = {'numerodepartidas': len(self.invoice_line_ids)}
        invoice_lines = []
        for line in self.invoice_line_ids:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue

            if not line.product_id.clave_producto:
                self.write({'proceso_timbrado': False})
                self.env.cr.commit()
                raise UserError(_('El producto %s no tiene clave del SAT configurado.') % (line.product_id.name))
            if not line.product_id.cat_unidad_medida.clave:
                self.write({'proceso_timbrado': False})
                self.env.cr.commit()
                raise UserError(_('El producto %s no tiene unidad de medida del SAT configurado.') % (line.product_id.name))

            price_wo_discount = line.price_unit * (1 - (line.discount / 100.0))

            taxes_prod = line.tax_ids.compute_all(price_wo_discount, currency=line.currency_id, quantity=line.quantity, product=line.product_id, partner=line.move_id.partner_id,)

            tax_ret = []
            tax_tras = []
            tax_items = {}
            tax_included = 0
            for taxes in taxes_prod['taxes']:
                tax = self.env['account.tax'].browse(taxes['id'])
                if not tax.impuesto:
                   self.write({'proceso_timbrado': False})
                   self.env.cr.commit()
                   raise UserError(_('El impuesto %s no tiene clave del SAT configurado.') % (tax.name))
                if not tax.tipo_factor:
                   self.write({'proceso_timbrado': False})
                   self.env.cr.commit()
                   raise UserError(_('El impuesto %s no tiene tipo de factor del SAT configurado.') % (tax.name))
                if tax.impuesto != '004':
                   key = taxes['id']
                   if tax.price_include or tax.amount_type == 'division':
                       tax_included += taxes['amount']

                   if taxes['amount'] >= 0.0:
                      if tax.tipo_factor == 'Exento':
                         tax_tras.append({'Base': self.set_decimals(taxes['base'], no_decimales_prod),
                                           'Impuesto': tax.impuesto,
                                           'TipoFactor': tax.tipo_factor,})
                      elif tax.tipo_factor == 'Cuota':
                         tax_tras.append({'Base': self.set_decimals(line.quantity, no_decimales_prod),
                                           'Impuesto': tax.impuesto,
                                           'TipoFactor': tax.tipo_factor,
                                           'TasaOCuota': self.set_decimals(tax.amount,6),
                                           'Importe': self.set_decimals(taxes['amount'], no_decimales_prod),})
                      else:
                         tax_tras.append({'Base': self.set_decimals(taxes['base'], no_decimales_prod),
                                           'Impuesto': tax.impuesto,
                                           'TipoFactor': tax.tipo_factor,
                                           'TasaOCuota': self.set_decimals(tax.amount / 100.0,6),
                                           'Importe': self.set_decimals(taxes['amount'], no_decimales_prod),})
                      tras_tot += taxes['amount']
                      val = {'tax_id': taxes['id'],
                             'base': taxes['base'] if tax.tipo_factor != 'Cuota' else line.quantity,
                             'amount': taxes['amount'],}
                      if key not in tax_grouped_tras:
                          tax_grouped_tras[key] = val
                      else:
                          tax_grouped_tras[key]['base'] += val['base'] if tax.tipo_factor != 'Cuota' else line.quantity
                          tax_grouped_tras[key]['amount'] += val['amount']
                   else:
                      tax_ret.append({'Base': self.set_decimals(taxes['base'], no_decimales_prod),
                                      'Impuesto': tax.impuesto,
                                      'TipoFactor': tax.tipo_factor,
                                      'TasaOCuota': self.set_decimals(tax.amount / 100.0 * -1, 6),
                                      'Importe': self.set_decimals(taxes['amount'] * -1, no_decimales_prod),})
                      ret_tot += taxes['amount'] * -1
                      val = {'tax_id': taxes['id'],
                             'base': taxes['base'],
                             'amount': taxes['amount'],}
                      if key not in tax_grouped_ret:
                          tax_grouped_ret[key] = val
                      else:
                          tax_grouped_ret[key]['base'] += val['base']
                          tax_grouped_ret[key]['amount'] += val['amount']
                else: #impuestos locales
                   if taxes['amount'] >= 0.0:
                      tax_local_tras_tot += taxes['amount']
                      tax_local_tras.append({'ImpLocTrasladado': tax.impuesto_local,
                                             'TasadeTraslado': self.set_decimals(tax.amount,2),
                                             'Importe': self.set_decimals(taxes['amount'], 2),})
                   else:
                      tax_local_ret_tot += taxes['amount']
                      tax_local_ret.append({'ImpLocRetenido': tax.impuesto_local,
                                            'TasadeRetencion': self.set_decimals(tax.amount * -1,2),
                                            'Importe': self.set_decimals(taxes['amount'] * -1, 2),})

            if tax_tras:
               tax_items.update({'Traslados': tax_tras})
            if tax_ret:
               tax_items.update({'Retenciones': tax_ret})

            total_wo_discount = round(line.price_unit * line.quantity - tax_included, no_decimales_prod)
            discount_prod = round(total_wo_discount - line.price_subtotal, no_decimales_prod) if line.discount else 0
            precio_unitario = round(total_wo_discount / line.quantity, no_decimales_prod)
            self.subtotal += total_wo_discount
            self.discount += discount_prod

            #probar con varios pedimentos
            pedimentos = []
            if line.pedimento:
                pedimento_list = line.pedimento.replace(' ','').split(',')
                for pedimento in pedimento_list:
                   if len(pedimento) != 15:
                      self.write({'proceso_timbrado': False})
                      self.env.cr.commit()
                      raise UserError(_('La longitud del pedimento debe ser de 15 dígitos.'))
                   pedimentos.append({'NumeroPedimento': pedimento[0:2] + '  ' + pedimento[2:4] + '  ' + pedimento[4:8] + '  ' + pedimento[8:]})

            product_string = line.product_id.code and line.product_id.code[:100] or ''
            if product_string == '':
               if line.name.find(']') > 0:
                  product_string = line.name[line.name.find('[')+len('['):line.name.find(']')] or ''
            description = line.name
            if line.name.find(']') > 0:
                 description = line.name[line.name.find(']') + 2:]

            if self.tipo_comprobante == 'T':
                invoice_lines.append({'cantidad': self.set_decimals(line.quantity,6),
                                      'unidad': line.product_id.cat_unidad_medida.descripcion,
                                      'NoIdentificacion': self.clean_text(product_string),
                                      'valorunitario': self.set_decimals(precio_unitario, no_decimales_prod),
                                      'importe': self.set_decimals(total_wo_discount, no_decimales_prod),
                                      'descripcion': self.clean_text(description),
                                      'ClaveProdServ': line.product_id.clave_producto,
                                      'ObjetoImp': '01' if factura_extranjera else line.product_id.objetoimp,
                                      'ClaveUnidad': line.product_id.cat_unidad_medida.clave})
            else:
                invoice_lines.append({'cantidad': self.set_decimals(line.quantity,6),
                                      'unidad': line.product_id.cat_unidad_medida.descripcion,
                                      'NoIdentificacion': self.clean_text(product_string),
                                      'valorunitario': self.set_decimals(precio_unitario, no_decimales_prod),
                                      'importe': self.set_decimals(total_wo_discount, no_decimales_prod),
                                      'descripcion': self.clean_text(description),
                                      'ClaveProdServ': line.product_id.clave_producto,
                                      'ClaveUnidad': line.product_id.cat_unidad_medida.clave,
                                      'Impuestos': tax_items and tax_items or '',
                                      'Descuento': self.set_decimals(discount_prod, no_decimales_prod),
                                      'ObjetoImp': '01' if factura_extranjera else line.product_id.objetoimp,
                                      'InformacionAduanera': pedimentos and pedimentos or '',
                                      'predial': line.predial and line.predial or '',})

        tras_tot = round(tras_tot, no_decimales)
        ret_tot = round(ret_tot, no_decimales)
        tax_local_tras_tot = round(tax_local_tras_tot, no_decimales)
        tax_local_ret_tot = round(tax_local_ret_tot, no_decimales)
        self.discount = round(self.discount, no_decimales)
        self.subtotal = self.roundTraditional(self.subtotal,no_decimales)
        if tax_grouped_tras or tax_grouped_ret:
                impuestos = {}
                retenciones = []
                traslados = []
                if tax_grouped_tras:
                   for line in tax_grouped_tras.values():
                       tax = self.env['account.tax'].browse(line['tax_id'])
                       if tax.tipo_factor == 'Exento':
                          tasa_tr = ''
                       elif tax.tipo_factor == 'Cuota':
                          tasa_tr = self.set_decimals(tax.amount, 6)
                       else:
                          tasa_tr = self.set_decimals(tax.amount / 100.0, 6)
                       traslados.append({'impuesto': tax.impuesto,
                                         'TipoFactor': tax.tipo_factor,
                                         'tasa': tasa_tr,
                                         'importe': self.set_decimals(line['amount'], no_decimales) if tax.tipo_factor != 'Exento' else '',
                                         'base': self.set_decimals(line['base'], no_decimales),
                                         'tax_id': line['tax_id'],
                                         })
                   impuestos.update({'translados': traslados, 'TotalImpuestosTrasladados': self.set_decimals(tras_tot, no_decimales)})
                if tax_grouped_ret:
                   for line in tax_grouped_ret.values():
                       tax = self.env['account.tax'].browse(line['tax_id'])
                       retenciones.append({'impuesto': tax.impuesto,
                                         'TipoFactor': tax.tipo_factor,
                                         'tasa': self.set_decimals(float(tax.amount) / 100.0 * -1, 6),
                                         'importe': self.set_decimals(line['amount'] * -1, no_decimales),
                                         'base': self.set_decimals(line['base'], no_decimales),
                                         'tax_id': line['tax_id'],
                                         })
                   impuestos.update({'retenciones': retenciones, 'TotalImpuestosRetenidos': self.set_decimals(ret_tot, no_decimales)})
                request_params.update({'impuestos': impuestos})
                self.tax_payment = json.dumps(impuestos)

        if tax_local_ret or tax_local_tras:
           if tax_local_tras and not tax_local_ret:
               request_params.update({'implocal10': {'TotaldeTraslados': self.set_decimals(tax_local_tras_tot, 2),
                                                     'TotaldeRetenciones': self.set_decimals(tax_local_ret_tot,2), 
                                                     'TrasladosLocales': tax_local_tras,}})
           if tax_local_ret and not tax_local_tras:
               request_params.update({'implocal10': {'TotaldeTraslados': self.set_decimals(tax_local_tras_tot,2), 
                                                     'TotaldeRetenciones': self.set_decimals(tax_local_ret_tot * -1,2), 
                                                     'RetencionesLocales': tax_local_ret,}})
           if tax_local_ret and tax_local_tras:
               request_params.update({'implocal10': {'TotaldeTraslados': self.set_decimals(tax_local_tras_tot,2),
                                                     'TotaldeRetenciones': self.set_decimals(tax_local_ret_tot * -1,2),
                                                     'TrasladosLocales': tax_local_tras,
                                                     'RetencionesLocales': tax_local_ret,}})

        if self.tipo_comprobante == 'T':
            request_params['factura'].update({'subtotal': '0.00','total': '0.00'})
            self.total_factura = 0
        else:
            self.total_factura = round(self.subtotal + tras_tot - ret_tot - self.discount + tax_local_ret_tot + tax_local_tras_tot,2)
            request_params['factura'].update({'descuento': self.set_decimals(self.discount, no_decimales),
                                              'subtotal': self.set_decimals(self.subtotal, no_decimales),
                                              'total':  self.set_decimals(self.total_factura, no_decimales)})

        request_params.update({'conceptos': invoice_lines})

        return request_params


    def _get_reconciled_info_JSON_values(self):
        self.ensure_one()
        foreign_currency = self.currency_id if self.currency_id != self.company_id.currency_id else False

        reconciled_vals = []
        pay_term_line_ids = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        partials = pay_term_line_ids.mapped('matched_debit_ids') + pay_term_line_ids.mapped('matched_credit_ids')
        for partial in partials:
            counterpart_lines = partial.debit_move_id + partial.credit_move_id
            # In case we are in an onchange, line_ids is a NewId, not an integer. By using line_ids.ids we get the correct integer value.
            counterpart_line = counterpart_lines.filtered(lambda line: line.id not in self.line_ids.ids)

            if foreign_currency and partial.currency_id == foreign_currency:
                amount = partial.amount_currency
                #amount_mxn = partial.amount * self.currency_id.with_context(date=self.invoice_date).rate
                amount_mxn = partial.amount * self.currency_rate
                #_logger.info('entra a amount_mxn %s', amount_mxn)
            else:
                #_logger.info('no entra a foraneo')
                amount = partial.company_currency_id._convert(partial.amount, self.currency_id, self.company_id, self.date)
                amount_mxn = partial.company_currency_id._convert(partial.amount, self.currency_id, self.company_id, self.date)

            if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                continue

            ref = counterpart_line.move_id.name
            if counterpart_line.move_id.ref:
                ref += ' (' + counterpart_line.move_id.ref + ')'

            reconciled_vals.append({
                'name': counterpart_line.name,
                'journal_name': counterpart_line.journal_id.name,
                'amount': amount,
                'amount_mxn': amount_mxn,
                'currency': self.currency_id.symbol,
                'digits': [69, self.currency_id.decimal_places],
                'position': self.currency_id.position,
                'date': counterpart_line.date,
                'payment_id': counterpart_line.id,
                'account_payment_id': counterpart_line.payment_id.id,
                'payment_method_name': counterpart_line.payment_id.payment_method_id.name if counterpart_line.journal_id.type == 'bank' else None,
                'move_id': counterpart_line.move_id.id,
                'ref': ref,
            })
        return reconciled_vals

    def set_decimals(self, amount, precision):
        if amount is None or amount is False:
            return None

        if precision > 2:
            return '%.*f' % (precision, amount)
        else:
            return '%.*f' % (precision, float_utils.float_round(amount,precision))
