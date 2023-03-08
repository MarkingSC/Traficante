import logging
from odoo import api, fields, models, _

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
    authorizers_uids = fields.Many2many('res.users', string='Additional authorizers', relation='authorization_policy_authorizers_rel')
    notified_uids = fields.Many2many('res.users', string='Notified users')
    additional_viewer_uids = fields.Many2many('res.users', string='Additional viewers', relation='authorization_policy_viewers_rel')


    @api.constrains('model_id')
    def _update_model_and_views(self):
        #_logger.info('***** Inicia _update_model_and_views *****')
        for policy in self:
            if policy.model_id:
                if 'x_current_authorization_id' not in self.env[policy.model_id.model]._fields:
                    # Creacion del campo de task_id en el modelo de destino
                    self.env['ir.model.fields'].create({
                        'field_description': '',
                        'model': policy.model_id.model,
                        'model_id': policy.model_id.id,
                        'name': 'x_current_authorization_id',
                        'state': 'manual',
                        'ttype': 'many2one',
                        'relation': 'authorization.task'
                    })

                    #_logger.info('***** CREÓ EL CAMPO *****')

                prev_action = self.env['ir.actions.server'].search([('code', '=', 'action = records._action_show_auth_form()'), ('model_id', '=', policy.model_id.id)], limit = 1)
                
                #_logger.info('***** prev_action:' + str(prev_action))

                if not prev_action:
                    # Crea una acción de ventana asociada al modelo
                    self.env['ir.actions.server'].create({
                        'xml_id': policy.model_id.model.replace('.','_')+'_auth_action',
                        'name': _('Ask for changes'),
                        'model_name': 'authorization.task',
                        'model_id': policy.model_id.id,
                        'binding_model_id': policy.model_id.id, 
                        'binding_view_types': 'form',
                        'binding_type': 'action',
                        'activity_user_type': 'generic',
                        'state': 'code',
                        'code': 'action = records._action_show_auth_form()',
                    })
                    
                    #_logger.info('***** CREÓ LA ACCION *****')

                    

