
from odoo import models, fields, api
import logging


_logger = logging.getLogger(__name__)
class ResPartner(models.Model):

    _inherit = 'res.partner'

    business_name = fields.Char(string='Business name')

    @api.onchange('type', 'parent_id')
    def _get_business_name_from_type(self):
        _logger.info('**** _get_business_name:16 ')
        if (self.parent_id):
            _logger.info('**** _get_business_name:18 ')
            if (self.parent_id.business_name):
                _logger.info('**** _get_business_name:20 ')
                self.business_name = self.parent_id.business_name

                if (self.type == 'invoice'):
                    _logger.info('**** _get_business_name:24 ')
                    self.name = self.parent_id.business_name
            else:
                _logger.info('**** _get_business_name:27 ')
                if (self.type == 'invoice'):
                    _logger.info('**** _get_business_name:29 ')
                    self.parent_id.write({"business_name": self.name})
                    self.business_name = self.name

    
    def write(self, vals):
        _logger.info('**** entra a write con vals: '+ str(vals))
        res = super(ResPartner, self).write(vals)
        if 'parent_id' in vals:
            _logger.info('**** se está cambiando el parent_id: '+ str(vals['parent_id']))
            self.business_name = self.parent_id.business_name
        return res


    @api.onchange('name')
    def _get_business_name_from_name(self):
        _logger.info('**** _get_business_name_from_name:34 ')
        if (self.parent_id and self.type == 'invoice'):
            _logger.info('**** _get_business_name_from_name:36: self.parent_id: ' + str(self.parent_id._origin))
            #parent = self.env['res.partner'].search([('id', '=', self.parent_id.id)], limit=1)
            
            self.parent_id._origin.write({"business_name": self.name})
            self._origin.business_name = self.name

    def _fields_sync(self, values):
        """ Sync commercial fields and address fields from company and to children after create/update,
        just as if those were all modeled as fields.related to the parent """
        _logger.info('**** _fields_sync ')
        # 1. From UPSTREAM: sync from parent
        if values.get('parent_id') or values.get('type') == 'contact':
            # 1a. Commercial fields: sync if parent changed
            if values.get('parent_id'):
                self._commercial_sync_from_company()
            # 1b. Address fields: sync if parent or use_parent changed *and* both are now set
            #if self.parent_id and self.type == 'contact':
            #    onchange_vals = self.onchange_parent_id().get('value', {})
            #    self.update_address(onchange_vals)

        # 2. To DOWNSTREAM: sync children
        self._children_sync(values)           


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
                _logger.info('**** current_partner ' + str(current_partner.display_name))
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
                    if 'invoice' in adr_pref and not result.get('invoice'):
                        result['invoice'] = current_partner
                    break
                current_partner = current_partner.parent_id

        # default to type 'contact' or the partner itself
        if result.get('delivery'):
            _logger.info('**** result.get(delivery) ' + str(result.get('delivery')))
        if result.get('invoice'):           
            _logger.info('**** result.get(invoice) ' + str(result.get('invoice')))
        default = result.get('contact', self.id or False)
        for adr_type in adr_pref:
            result[adr_type] = result.get(adr_type) or default
        return result