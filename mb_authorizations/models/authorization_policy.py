import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class AuthorizationPolicy(models.Model):
    _name = "authorization.policy"

    name = fields.Char(required=True)
    before_condition = fields.Char(string='Before condition')
    after_condition = fields.Char(string='After condition')
    model_id = fields.Many2one('ir.model', string='Model', required=True)

    default_description = fields.Char(string="Default description")
    default_priority = fields.Selection([
            ('0', 'Low'),
            ('1', 'Medium'),
            ('2', 'High'),
            ('3', 'Very High'),
        ], string='Priority', index=True, default="0")

    authorizer_uid = fields.Many2one('res.users', string='Authorizator user', required=True)
    notified_uids = fields.Many2many('res.users', string='Recipients', required=True)
