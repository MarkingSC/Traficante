
from dataclasses import field
import logging
from odoo import models, fields, api, _, exceptions
import odoo
from datetime import timedelta, datetime
import calendar
import pytz
from odoo.exceptions import AccessError, UserError, ValidationError

datetime.today()

_logger = logging.getLogger(__name__)

class salesOrigin(models.Model):
    _name = 'sales.origin'
    _description = 'Sales origin'

    # nombre del registro de la meta
    name = fields.Char(string='Name', required=True, help='Set the name of the origin.')
    # descripcion del registro de la meta
    description = fields.Char(string='Description', required=True, help='Set the description.')

class saleOrder(models.Model):
    _inherit = 'sale.order'

    # Origen de venta para reportes
    sales_origin_id = fields.Many2one(string='Origin', help='Set sales origin for reporting', comodel_name='sales.origin')