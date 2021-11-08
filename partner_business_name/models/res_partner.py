
from odoo import models, fields, api
import logging


_logger = logging.getLogger(__name__)
class ResPartner(models.Model):

    _inherit = 'res.partner'

    business_name = fields.Char(string='Business name')

    @api.onchange('type', 'parent_id')
    def _get_business_name_from_type(self):
        _logger.info('**** _get_business_name:15 ')
        if (self.parent_id):
            _logger.info('**** _get_business_name:17 ')
            if (self.parent_id.business_name):
                _logger.info('**** _get_business_name:19 ')
                self.business_name = self.parent_id.business_name

                if (self.type == 'invoice'):
                    _logger.info('**** _get_business_name:23 ')
                    self.name = self.parent_id.business_name
            else:
                _logger.info('**** _get_business_name:26 ')
                if (self.type == 'invoice'):
                    _logger.info('**** _get_business_name:28 ')
                    self.parent_id.write({"business_name": self.name})
                    self.business_name = self.name

    @api.onchange('name')
    def _get_business_name_from_name(self):
        _logger.info('**** _get_business_name_from_name:34 ')
        if (self.parent_id and self.type == 'invoice'):
            _logger.info('**** _get_business_name_from_name:36: self.parent_id: ' + str(self.parent_id._origin))
            #parent = self.env['res.partner'].search([('id', '=', self.parent_id.id)], limit=1)
            
            self.parent_id._origin.write({"business_name": self.name})
            self._origin.business_name = self.name

        