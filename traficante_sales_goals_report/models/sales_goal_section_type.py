
import logging
from typing_extensions import Required
from odoo import models, fields, api, _, exceptions
import odoo
from datetime import timedelta, datetime
import pytz
from odoo.exceptions import AccessError, UserError, ValidationError

datetime.today()

_logger = logging.getLogger(__name__)

class SalesGoalSectionType(models.Model):
    _name = 'sales.goal.section.type'
    _description = 'Section type for goals'

    name = fields.Char(string='Name', required=True, help='Set the name of the section')
    description = fields.Char(string='Description', required=True, help='Set the description of the section')
    active = fields.Boolean(default=True, help="Set active to false to hide the section type without removing it.")

    domain = fields.Char(string='Conditions', help='Set conditions for invoice lines to meet')


