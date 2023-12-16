# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from email.policy import default
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class BaseModelExtend(models.AbstractModel):
    _inherit = 'base'

    def unlink(self):
        #evaluar condicion antes

        res = super(BaseModelExtend, self).unlink()

        #evaluar condicion despues

        #crear tarea

        return res

    def _get_before_values(self, vals):
        return_values = {}
        for value in vals:
            return_values[value] = self[value]
        return return_values

    def write(self, vals):
        # evaluar condicion antes
        # busca políticas de autorización que coincidan
        
        
        all_policies = self.env['authorization.policy'].sudo().search([])
        all_policies_models = all_policies.mapped('model_id.model')

        _logger.info('***** Entra al write de autorizaciones **** ')

        # Si el modelo del registro modificado tiene una política entonces lo somete, si no no
        if self._name in all_policies_models:

            matching_policies_1 = []
            matching_policies_2 = []
            all_policies_this_model = all_policies.filtered(lambda record: record.model_id.model == self._name)
            changed_field_policies = all_policies_this_model.filtered(lambda record: record.changed_field != False)
            double_check_policies = all_policies_this_model.filtered(lambda record: record.before_condition and record.after_condition)

            for policy in changed_field_policies:
                for field in vals:
                    if field == policy.changed_field:
                        matching_policies_1.append(policy)

            before_values = self._get_before_values(vals)

            if changed_field_policies:
                for policy in matching_policies_1:
                    _logger.info('***** Coincide la policita de change field **** ')
                    # Aqui tiene que generar la creación de una tarea y regresar el registro a los valores anteriores.
                    if self.env.user.id != policy.authorizer_uid.id and self.env.user.id not in policy.authorizers_uids.mapped('id'):

                        # obtiene una autorización ya existente
                        prev_auth_task = self.env['authorization.task'].search([('model_id', '=', policy.model_id.id), ('res_id', '=', self.id), ('state', '=', 'draft')], limit=1)
                        # si ya existe una, no deja avanzar
                        if prev_auth_task != False and prev_auth_task.id:
                            #self.write(before_values)
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
                            
                            #self.write(before_values)
                            # Asocia la nueva autorización
                            self.write({'x_current_authorization_id': created_task.id})

                        self.env.cr.commit()
                        raise UserError(_('Some changes require an authorization to continue. Please clic Actions/Ask for changes to specify a reason and continue.'))

                    else:
                        _logger.info('***** Fue un cambio realizado por un autorizador, entonces procede con el cambio **** ')


            _logger.info('*** Evaluó las condiciones de change field ***')

            matching_policies_1 = []
            matching_policies_2 = []

            if double_check_policies:
                #evaluar condicion antes
                for policy in double_check_policies:
                    if policy.before_condition:
                        matches_condition_1 = False 
                        matches_condition_1 = self.filtered(lambda record: eval(policy.before_condition))
                        if matches_condition_1:
                            matching_policies_1.append(policy)                

                before_values = self._get_before_values(vals)

                res = super(BaseModelExtend, self).write(vals)

                #evaluar condicion despues
                for policy in double_check_policies:
                    if policy.after_condition:
                        matches_condition_2 = False
                        matches_condition_2 = self.filtered(lambda record: eval(policy.after_condition))
                        if matches_condition_2:
                            matching_policies_2.append(policy)

                _logger.info('***** Terminó de evaluar condiciones **** ')
                #crear tarea
                # si los cambios coinciden en ambos momentos, asigna los valores para ejecutar la creación de una autorización
                for policy in matching_policies_1:
                    if policy in matching_policies_2:
                        _logger.info('***** Coinciden las 2 politicas **** ')
                        # Aqui tiene que generar la creación de una tarea y regresar el registro a los valores anteriores.
                        if self.env.user.id != policy.authorizer_uid.id and self.env.user.id not in policy.authorizers_uids.mapped('id'):

                            # obtiene una autorización ya existente
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

                            self.env.cr.commit()
                            raise UserError(_('Some changes require an authorization to continue. Please clic Actions/Ask for changes to specify a reason and continue.'))

                        else:
                            _logger.info('***** Fue un cambio realizado por un autorizador, entonces procede con el cambio **** ')

            return res
        else:
            return super(BaseModelExtend, self).write(vals)
    
    def _action_show_auth_form(self):
        for record in self:
            if record.x_current_authorization_id.id != False:
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