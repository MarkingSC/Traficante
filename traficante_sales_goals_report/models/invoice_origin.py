
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

class invoiceOrigin(models.Model):
    _name = 'invoice.origin'
    _description = 'Invoicing origin'

    # nombre del registro de la meta
    name = fields.Char(string='Name', required=True, help='Set the name of the origin.')
    # descripcion del registro de la meta
    description = fields.Char(string='Description', required=True, help='Set the description.')

class accountMove(models.Model):
    _inherit = 'account.move'

    # Origen de facturacion para reportes
    invoice_origin_id = fields.Many2one(string='Origin', help='Set invoicing origin for reporting', comodel_name='invoice.origin')