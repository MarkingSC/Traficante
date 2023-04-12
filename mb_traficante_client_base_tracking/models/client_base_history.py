
import logging
import pytz
from datetime import  datetime, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


_logger = logging.getLogger(__name__)
class ClientBaseHistory(models.Model):

    _name = 'client.base.history'

    partner_id = fields.Many2one('res.partner', string="Customer")
    user_id = fields.Many2one('base.user', string="Executive id")
    user_name = fields.Char(string="Executive")
    assignment_date = fields.Datetime(string="Assignment date")

    @api.model
    def create(self, vals):
        vals['assignment_date'] = datetime.now()
        _logger.debug('vals[user_id]' + str (vals['user_id']))
        user = self.env['res.users'].search([('id', '=', vals['user_id'])])
        vals['user_name'] = user.name

        row = super(ClientBaseHistory, self).create(vals)        

        return row