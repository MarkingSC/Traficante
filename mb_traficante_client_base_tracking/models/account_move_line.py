
import logging
import pytz
from datetime import  datetime, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


_logger = logging.getLogger(__name__)
class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    executive_tracking = fields.Char(string='Salesperson', compute='_get_executive_tracking', store=True)

    @api.depends('partner_id')
    def _get_executive_tracking(self):
        for line in self:
            line.executive_tracking = line.partner_id.executive_tracking