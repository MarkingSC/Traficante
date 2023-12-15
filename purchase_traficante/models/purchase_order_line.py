
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)
class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.model
    def _get_received_date(self):
        _logger.debug("**** self en _get_received_date: " + str(self))
        purchase_order = self.order_id
        _logger.debug("**** purchase_order en _get_received_date: " + str(purchase_order))
        if purchase_order and len(purchase_order.picking_ids)>0:
            stock_move = purchase_order.picking_ids[0]
            _logger.debug("**** stock_move en _get_received_date: " + str(stock_move))
            self.received_date = stock_move.date_done
        else:
            _logger.debug("**** no hay picking_ids en _get_received_date para self:" + str(self))
            self.received_date = None

    @api.model
    def _get_received_name(self):
        for record in self:
            #_logger.info("**** self en _get_received_name: " + str(self))
            purchase_order = record.order_id
            #_logger.info("**** purchase_order en _get_received_name: " + str(purchase_order))
            if purchase_order and len(purchase_order.picking_ids) > 0:
                stock_move = purchase_order.picking_ids[0]
                #_logger.info("**** stock_move en _get_received_name: " + str(stock_move))
                record.received_name = stock_move.name
            else:
               # _logger.info("**** no hay picking_ids en _get_received_name para self:" + str(self))
                record.received_name = None

    @api.depends('order_id.receipt_type')
    def _get_receipt_type(self):
        for record in self:
            _logger.debug("**** self en _get_receipt_type: " + str(record))
            purchase_order = record.order_id
            _logger.debug("**** purchase_order en _get_receipt_type: " + str(purchase_order))
            if purchase_order:
                _logger.debug("**** purchase_order en _get_receipt_type: " + str(purchase_order))
                record.receipt_type = purchase_order.receipt_type
            else:
                _logger.debug("**** no hay purchase_order en _get_receipt_type para self:" + str(record))
                record.receipt_type = 'regular'

    receipt_type = fields.Selection(selection = [('regular','Regular'),('credito','Crédito'),('consigna','Consigna')], string='Tipo de recepción', compute=_get_receipt_type, store=True)

    partner_id = fields.Many2one(string="Proveedor", comodel_name="res.partner", related="order_id.partner_id")
    received_date = fields.Date(string="Fecha de recepción", default=_get_received_date)
    received_name = fields.Char(string="Nombre de recepción", compute='_get_received_name', store=False)

    origin = fields.Char(string='Documento origen', compute='_get_origin', store=False)
    elaboration_date = fields.Date(string='Fecha de elaboración', compute='_get_elaboration_date', store=False)

    def _get_origin(self):
        for line in self:
            originMap = line.order_id.mapped('name')
            line.origin = ','.join(originMap)

    def _get_elaboration_date(self):
        for line in self:
            dateMap = line.order_id.mapped('date_approve')
            formattedDates = [date.date().strftime('%Y-%m-%d') for date in dateMap if isinstance(date, datetime)]
            line.elaboration_date = ','.join(formattedDates)