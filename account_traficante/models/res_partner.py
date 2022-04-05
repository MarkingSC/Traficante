from odoo import models, fields, api
import logging


_logger = logging.getLogger(__name__)
class ResPartner(models.Model):

    _inherit = 'res.partner'

    delivery_address = fields.Many2one('res.partner', string='Delivery address', compute="_address_get_delivery", store = True)

    # Obtiene la dirección de entrega para la factura
    @api.depends('child_ids', 'name', 'street', 'street2', 'city', 'state_id', 'zip', 'country_id')
    def _address_get_delivery(self):
        for record in self:
            record.delivery_address = record.address_get(adr_pref=['delivery']).get('delivery')