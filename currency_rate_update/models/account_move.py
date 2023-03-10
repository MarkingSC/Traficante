from datetime import datetime

from dateutil.relativedelta import relativedelta

import logging
from odoo import api, fields, models, _
from odoo.addons.base.models import decimal_precision as dp

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Campo específico para la implementación de TRaficante
    currency_rate = fields.Float(string="Rate", digits = 0, default=lambda self: 1/self.currency_id.rate if self.currency_id.rate > 0 else self.currency_id.rate)

    @api.onchange('currency_id')
    def _get_currency_rate(self):
        self.currency_rate =  1/self.currency_id.rate if self.currency_id.rate > 0 else self.currency_id.rate

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if 'currency_id' in vals:
            self._get_currency_rate()
        return res
    
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        res._get_currency_rate()
        return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        _logger.info('**** ESTA ENTRANDO A _onchange_product_id ****')

        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue

            line.name = line._get_computed_name()
            line.account_id = line._get_computed_account()
            taxes = line._get_computed_taxes()
            if taxes and line.move_id.fiscal_position_id:
                taxes = line.move_id.fiscal_position_id.map_tax(taxes, partner=line.partner_id)
            line.tax_ids = taxes
            line.product_uom_id = line._get_computed_uom() 
            line.price_unit = line._get_computed_price_unit()

        if len(self) == 1:
            return {'domain': {'product_uom_id': [('category_id', '=', self.product_uom_id.category_id.id)]}}

    
    @api.onchange('price_unit')
    def _onchange_price_unit_set_currency_price(self):
        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue

            pesos = line.product_id.list_price
            dolares = line._get_computed_price_unit()
            tasa = (dolares / pesos)
            
            _logger.info('precio de lista del producto: ' + str(pesos))
            _logger.info('precio unitario en moneda destino: ' + str(dolares))
            _logger.info('tasa de cambio personalizada: ' + str(tasa))

            unidad_tasa = tasa / (pesos / dolares)
            
            custom_tasa = line.move_id.currency_rate
            nueva_tasa_referencia = unidad_tasa * custom_tasa

            nuevo_precio_lista = dolares / nueva_tasa_referencia

            _logger.info('nuevo precio de lista del producto: ' + str(nuevo_precio_lista))

            line.product_id.sudo().write({
                'list_price': nuevo_precio_lista
            })
            
            #line.product_id.list_price = nuevo_precio_lista

            line.price_unit = line._get_computed_price_unit()
            _logger.info('nuevo precio unitario en moneda destino: ' + str(line.price_unit))

            line.product_id.sudo().write({
                'list_price': pesos
            })
            #line.product_id.list_price = pesos
            _logger.info('Regresó el precio de lista del producto: ' + str(pesos))

    # -------------------------------------------------------------------------
    # ONCHANGE METHODS
    # -------------------------------------------------------------------------

    @api.onchange('amount_currency', 'currency_id', 'debit', 'credit', 'tax_ids', 'account_id', 'price_unit')
    def _onchange_mark_recompute_taxes(self):
        _logger.info('*** _onchange_mark_recompute_taxes ***')
        ''' Recompute the dynamic onchange based on taxes.
        If the edited line is a tax line, don't recompute anything as the user must be able to
        set a custom value.
        '''
        for line in self:
            if not line.tax_repartition_line_id:
                line.recompute_tax_line = True
            
            # --
            pesos = line.product_id.list_price
            dolares = line._get_computed_price_unit()

            if pesos and dolares:
                
                _logger.info('precio de lista del producto: ' + str(pesos))
                _logger.info('precio unitario en moneda destino: ' + str(dolares))
                tasa = (dolares / pesos)
                _logger.info('tasa de cambio personalizada: ' + str(tasa))

                unidad_tasa = tasa / (pesos / dolares)
                
                custom_tasa = line.move_id.currency_rate
                nueva_tasa_referencia = unidad_tasa * custom_tasa

                nuevo_precio_lista = dolares / nueva_tasa_referencia

                _logger.info('nuevo precio de lista del producto: ' + str(nuevo_precio_lista))
                #line.product_id.list_price = nuevo_precio_lista

                line.product_id.sudo().write({
                    'list_price': nuevo_precio_lista
                })

                line.price_unit = line._get_computed_price_unit()
                _logger.info('nuevo precio unitario en moneda destino: ' + str(line.price_unit))

                line.product_id.sudo().write({
                    'list_price': pesos
                })
                #line.product_id.list_price = pesos
                _logger.info('Regresó el precio de lista del producto: ' + str(pesos))
                
            # --
