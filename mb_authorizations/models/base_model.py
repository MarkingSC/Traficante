# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from email.policy import default
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

import logging
#_logger = logging.getLogger(__name__)

class BaseModelExtend(models.AbstractModel):
    _inherit = 'base'

    def unlink(self):
        #evaluar condicion antes

        res = super(BaseModelExtend, self).unlink()

        #evaluar condicion despues

        #crear tarea

        return res

    def _get_before_values(self, vals):
        #_logger.info('***** Entra a _get_before_values con values: ' + str(vals))
        return_values = {}
        for value in vals:
            return_values[value] = self[value]
        #_logger.info('***** Entra a return_values: ' + str(return_values))
        return return_values

    def write(self, vals):
        #_logger.info('***** Entra al write de base model con vals: ' + str(vals))
        # evaluar condicion antes
        # busca políticas de autorización que coincidan
        
        matching_policies_1 = []
        matching_policies_2 = []
        all_policies = self.env['authorization.policy'].sudo().search([])
        all_policies_models = all_policies.mapped('model_id.model')

        #_logger.info('***** all_policies_models: ' + str(all_policies_models))
        #_logger.info('***** nombre del modelo actual: ' + str(self._name))

        # Si el modelo del registro modificado tiene una política entonces lo somete, si no no
        if self._name in all_policies_models:

            #_logger.info('***** self: ' + str(self))
            #_logger.info('***** self.name: ' + str(self.name))
            active_ids = self._context.get('active_ids') or self._context.get('active_id')
            #_logger.info('***** active_ids: ' + str(active_ids))


            for policy in all_policies:
                #_logger.info('***** iterando política: ' + str(policy.name))
                matches_condition_1 = False
                matches_condition_1 = self.filtered(lambda record: eval(policy.before_condition))
                #_logger.info('***** hace match con la condición antes?: ' + str(matches_condition_1))
                if matches_condition_1:
                    matching_policies_1.append(policy)

            #_logger.info('***** matches_condition_1: ' + str(matches_condition_1))

            before_values = self._get_before_values(vals)

            #_logger.info('***** self.active: ' + str(self.active))
            #_logger.info('***** vals: ' + str(vals))
            res = super(BaseModelExtend, self).write(vals)
            #_logger.info('***** self.active: ' + str(self.active))
            #_logger.info('***** res: ' + str(res))

            #evaluar condicion despues
            for policy in all_policies:
                #_logger.info('***** iterando política: ' + str(policy.name))
                matches_condition_2 = False
                matches_condition_2 = self.filtered(lambda record: eval(policy.after_condition))
                #_logger.info('***** hace match con la condición despues?: ' + str(matches_condition_2))
                if matches_condition_2:
                    matching_policies_2.append(policy)

            #_logger.info('***** matches_condition_2: ' + str(matches_condition_2))

            #crear tarea
            #_logger.info('***** matching_policies_1: ' + str(matches_condition_1))
            #_logger.info('***** matching_policies_2: ' + str(matches_condition_2))

            # si los cambios coinciden en ambos momentos, asigna los valores para ejecutar la creación de una autorización
            for policy in matching_policies_1:
                #_logger.info('***** itera matching_policies_1 **** ')
                if policy in matching_policies_2:
                    #_logger.info('***** se cumplieron ambas condiciones de la política: ' + str(policy.name))
                    #_logger.info('***** policy.id: ' + str(policy.id))
                    #_logger.info('***** policy.model_id.id: ' + str(policy.model_id.id))
                    #_logger.info('***** self.id: ' + str(self.id))
                    #_logger.info('***** self.env.user.id: ' + str(self.env.user.id))
                    #_logger.info('***** policy.authorizer_uid.id: ' + str(policy.authorizer_uid.id))

                    # Aqui tiene que generar la creación de una tarea y regresar el registro a los valores anteriores.
                    if self.env.user.id != policy.authorizer_uid.id and self.env.user.id not in policy.authorizers_uids.mapped('id'):
                        #_logger.info('***** no fue un cambio realizado por un autorizador, entonces crea una tarea **** ')

                        # obtiene una acutorización ya existente
                        prev_auth_task = self.env['authorization.task'].search([('model_id', '=', policy.model_id.id), ('res_id', '=', self.id), ('state', '=', 'draft')], limit=1)
                        # si ya existe una, no deja avanzar
                        if prev_auth_task != False and prev_auth_task.id:
                            self.write(before_values)
                            self.env.cr.commit()
                            raise UserError(_('Some changes need to be authorized, but there is an existing authorization proceess for this record. Please check authorizations to send.'))
                        else:
                            # si no existe entonces crea una nueva
                            created_task = self.env['authorization.task'].create({
                                'policy_id': policy.id,
                                'new_vals': vals,
                                'model_id': policy.model_id,
                                'res_id': self.id,
                                'show_form': True,
                                'applicant_uid': self.env.user.id,
                                'assigned_uid': policy.authorizer_uid.id
                            })
                            
                            self.write(before_values)
                            # Asocia la nueva autorización
                            self.write({'x_current_authorization_id': created_task.id})

                        #self.flush()
                        self.env.cr.commit()
                        raise UserError(_('Some changes require an authorization to continue. Please clic Actions/Ask for changes to specify a reason and continue.'))

                    else:
                        _logger.info('***** Fue un cambio realizado por un autorizador, entonces procede con el cambio **** ')

            #_logger.info('***** Termina write de base model *****')

            return res
        else:
            #_logger.info('***** Termina write de base model *****')
            return super(BaseModelExtend, self).write(vals)
    
    def _action_show_auth_form(self):
        #_logger.info('***** Inicia _action_show_auth_form *****')
        for record in self:
            #_logger.info('***** record.x_current_authorization_id: ' + str(record.x_current_authorization_id))
            if record.x_current_authorization_id.id != False:
                #_logger.info('***** record.x_current_authorization_id.id: ' + str(record.x_current_authorization_id.id))
                return {
                    'title': 'Ask for authorization',
                    'type': 'ir.actions.act_window',
                    'res_model': 'authorization.task',
                    'target': 'new',
                    'views': [[False, 'form']],
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id': self.env.ref('mb_authorizations.view_authorization_task_wizard_form').id,
                    'res_id': record.x_current_authorization_id.id
                }
            else:
                raise UserError(_('There is no authorization pending.'))