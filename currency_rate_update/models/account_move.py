from datetime import datetime

from dateutil.relativedelta import relativedelta

import logging
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.addons.base.models import decimal_precision as dp

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Campo específico para la implementación de TRaficante
    currency_rate = fields.Float(string="Rate", digits=0, default=lambda self: 1 / self.currency_id.rate if self.currency_id.rate > 0 else self.currency_id.rate)

    today = fields.Date.today()

    @api.onchange('currency_id')
    def _get_currency_rate(self):
        #self.currency_rate = 1 / self.currency_id.rate if self.currency_id.rate > 0 else self.currency_id.rate
        #_logger.info('***** TASA ACTUAL *****: ' + str(self.currency_id.rate))
        # _logger.info('***** FECHA DE LA TASA *****: ' + str(self.currency_id.rate_ids.name))

        today = fields.Date.today()
        currency = self.currency_id.name
        # verifica si el dia actual es lunes, de ser así toma la tasa del viernes, si no toma la actual
        if today.weekday() == 0 and currency != "MXN":
            #_logger.info('***** es lunes *****: ')
            latest_rate = sorted(self.currency_id.rate_ids, key=lambda r: r.id)[-2]
            self.currency_rate = 1 / latest_rate.rate if latest_rate.rate > 0 else latest_rate.rate
            #_logger.info('***** tasa del viernes  *****: ' + str(latest_rate.rate))
        else:
            #_logger.info('***** no es lunes *****: ')
            self.currency_rate = 1 / self.currency_id.rate if self.currency_id.rate > 0 else self.currency_id.rate
            #_logger.info('***** tasa actual *****: ' + str(self.currency_id.rate))

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

            standard_price =  line.product_id.standard_price
            _logger.info('standard_price: ' + str(standard_price))

            line.price_unit = line.product_id.standard_price

        if len(self) == 1:
            return {'domain': {'product_uom_id': [('category_id', '=', self.product_uom_id.category_id.id)]}}

    '''
    @api.onchange('price_unit')
    def _onchange_price_unit_set_currency_price(self):
        _logger.info('*** _onchange_price_unit_set_currency_price ***')
        for line in self:
            if not line.tax_repartition_line_id:
                line.recompute_tax_line = True
    '''
       
    # -------------------------------------------------------------------------
    # ONCHANGE METHODS
    # -------------------------------------------------------------------------


    #@api.onchange('amount_currency', 'currency_id', 'debit', 'credit', 'tax_ids', 'account_id')
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
            
            pesos = line.product_id.standard_price

            price_unit_line = line.price_unit
            _logger.info('price_unit_line: ' + str(price_unit_line))
            
            pesos = price_unit_line if price_unit_line != pesos else pesos

            custom_tasa = line.move_id.currency_rate

            nuevo_precio_lista = pesos / custom_tasa

            _logger.info('nuevo precio de lista del producto: ' + str(nuevo_precio_lista))

            #line.price_unit = nuevo_precio_lista
                     
