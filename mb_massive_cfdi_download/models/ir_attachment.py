import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)
class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    invoice_id = fields.Many2one('account.move', string='Invoice', compute="_get_inv_defaults", store = True)
    partner_id = fields.Many2one('res.partner', string='Customer', compute="_get_inv_defaults", store = True)
    invoice_date = fields.Date(string='Invoice date', compute="_get_inv_defaults", store = False)
    partner_vat = fields.Char(string='VAT', compute="_get_inv_defaults", store = False)
    #company_id

    # Obtiene la dirección de entrega para la factura
    @api.depends('res_model', 'res_id')
    def _get_inv_defaults(self):
        for record in self:
            if record.res_model == 'account.move':
                record.invoice_id = self.env['account.move'].search([('id', '=', record.res_id)])
                record.partner_id = record.invoice_id.partner_id
                record.invoice_date = record.invoice_id.date
                record.partner_vat = record.partner_id.vat
            