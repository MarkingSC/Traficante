
import logging
import pytz
from datetime import  datetime, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


_logger = logging.getLogger(__name__)
class ResPartner(models.Model):

    _inherit = 'res.partner'
    _rec_name = 'display_name'

    executive_tracking = fields.Char(string='Tracking', store = True)
    client_base_history_ids = fields.One2many('client.base.history', 'partner_id', 'Executive history')


    def write(self, vals):

        val_executive_tracking = ''

        if 'user_id' in vals:
            if self.user_id.name:
                _logger.info(' *** self.user_id.name: ' + str(self.user_id.name))
                _logger.info(' *** self.executive_tracking: ' + str(self.executive_tracking))
                if self.executive_tracking:
                    val_executive_tracking = self.executive_tracking + ' > ' + self.user_id.name
                else:   
                    val_executive_tracking = self.user_id.name
            else:
                if self.executive_tracking:
                    val_executive_tracking = self.executive_tracking + ' > ' + 'Sin asignar'
                else:
                    val_executive_tracking = ''

        _logger.info(' *** val_executive_tracking: ' + str(val_executive_tracking))

        res = super(ResPartner, self).write(vals)

        if 'user_id' in vals:
            if self.user_id.name:
                _logger.info(' *** self.user_id.name: ' + str(self.user_id.name))
                _logger.info(' *** val_executive_tracking: ' + str(val_executive_tracking))
                if val_executive_tracking:
                    val_executive_tracking = val_executive_tracking + ' > ' + self.user_id.name
                else:   
                    val_executive_tracking = self.user_id.name
            else:
                if val_executive_tracking:
                    val_executive_tracking = val_executive_tracking + ' > ' + 'Sin asignar'
                else:
                    val_executive_tracking = ''

            _logger.info(' *** val_executive_tracking: ' + str(val_executive_tracking))
            self.executive_tracking = val_executive_tracking

            self.env['client.base.history'].sudo().create({'partner_id': self.id, 'user_id': self.user_id.id})

        return res

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        
        if 'user_id' in vals and vals['user_id']:
            self.executive_tracking = str(self.user_id.name if self.user_id.name else '')
            self.env['client.base.history'].sudo().create({'partner_id': self.id, 'user_id': self.user_id.id})

        return res