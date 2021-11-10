
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

    def address_get(self, adr_pref=None):
        """ Find contacts/addresses of the right type(s) by doing a depth-first-search
        through descendants within company boundaries (stop at entities flagged ``is_company``)
        then continuing the search at the ancestors that are within the same company boundaries.
        Defaults to partners of type ``'default'`` when the exact type is not found, or to the
        provided partner itself if no type ``'default'`` is found either. """
        adr_pref = set(adr_pref or [])
        if 'contact' not in adr_pref:
            adr_pref.add('contact')
        _logger.info('**** address_get:51 ' + str(adr_pref))
        result = {}
        visited = set()
        for partner in self:
            current_partner = partner
            while current_partner:
                to_scan = [current_partner]
                # Scan descendants, DFS
                while to_scan:
                    record = to_scan.pop(0)
                    visited.add(record)
                    if record.type in adr_pref and not result.get(record.type):
                        result[record.type] = record.id
                    if len(result) == len(adr_pref):
                        result[record.type] = record.id
                        return result
                    to_scan = [c for c in record.child_ids
                                 if c not in visited
                                 if not c.is_company] + to_scan

                # Continue scanning at ancestor if current_partner is not a commercial entity
                if 'delivery' in adr_pref and not result.get('delivery'):
                        result['delivery'] = current_partner

                if current_partner.is_company or not current_partner.parent_id:
                    break
                current_partner = current_partner.parent_id

        # default to type 'contact' or the partner itself
        default = result.get('contact', self.id or False)
        for adr_type in adr_pref:
            result[adr_type] = result.get(adr_type) or default
        return result