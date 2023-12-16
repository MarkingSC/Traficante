
import logging
from odoo import models, fields, api, _, exceptions
from datetime import timedelta, datetime
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from odoo.tools.misc import OrderedSet

datetime.today()

_logger = logging.getLogger(__name__)

class stockInventory(models.Model):
    _inherit = 'stock.inventory'

    def action_validate(self):
        _logger.info('*** Entra a action_validate de stock.inventory ***')

        if not self.exists():
            return

        auth_policy = self.env['authorization.policy'].search([('model_id', '=', 'stock.inventory'),('after_condition', '=', "record.state == 'done'")])

        ## Si hay una politica y el usuario no es autorizador de autorización entonces solo cambia el campo para que se cree la tarea de autorización. 
        if auth_policy and self.env.user.id != auth_policy.authorizer_uid.id and self.env.user.id not in auth_policy.authorizers_uids.mapped('id'):
            self.write({'state': 'done'});
            return
        ## Y si no hay una politica o el usuario si es autorizador entonces sigue con el proceso normal. 
        else:
            self.ensure_one()
            if not self.user_has_groups('stock.group_stock_manager'):
                raise UserError(_("Only a stock manager can validate an inventory adjustment."))
            if self.state != 'confirm':
                raise UserError(_(
                    "You can't validate the inventory '%s', maybe this inventory " +
                    "has been already validated or isn't ready.") % (self.name))
            inventory_lines = self.line_ids.filtered(lambda l: l.product_id.tracking in ['lot', 'serial'] and not l.prod_lot_id and l.theoretical_qty != l.product_qty)
            lines = self.line_ids.filtered(lambda l: float_compare(l.product_qty, 1, precision_rounding=l.product_uom_id.rounding) > 0 and l.product_id.tracking == 'serial' and l.prod_lot_id)
            if inventory_lines and not lines:
                wiz_lines = [(0, 0, {'product_id': product.id, 'tracking': product.tracking}) for product in inventory_lines.mapped('product_id')]
                wiz = self.env['stock.track.confirmation'].create({'inventory_id': self.id, 'tracking_line_ids': wiz_lines})
                return {
                    'name': _('Tracked Products in Inventory Adjustment'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'views': [(False, 'form')],
                    'res_model': 'stock.track.confirmation',
                    'target': 'new',
                    'res_id': wiz.id,
                }
            self._action_done()
            self.line_ids._check_company()
            self._check_company()
            return True