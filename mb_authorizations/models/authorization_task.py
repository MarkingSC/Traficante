from asyncio import Task
from datetime import datetime
from email.policy import default
import logging
from odoo.http import request
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AuthorizationTask(models.Model):
    _name = "authorization.task"
    #_inherit = ['mail.thread.cc', 'mail.thread.blacklist', 'mail.activity.mixin']
    _order = "priority desc, id desc"
    _inherit=['mail.thread', 'mail.activity.mixin']

    @api.depends('policy_id','res_id','model_id')
    def _get_default_name(self):
        for record in self:
            _logger.info('***** Entra a _get_default_name *****')
            _logger.info('***** record.res_id: ' + str(record.res_id))
            _logger.info('***** record.policy_id: ' + str(record.policy_id))
            _logger.info('***** record.model_id: ' + str(record.model_id))

            if record.res_id and record.policy_id and record.model_id:
                _logger.info('***** record.model_id: ' + str(record.model_id.model))
                rel_record = self.env[record.model_id.model].search([('id', '=', record.res_id)], limit = 1)
                _logger.info('***** rel_record: ' + str(rel_record) + str(rel_record.name))
                new_name = record.policy_id.default_description + ' ' + rel_record.name
                record.write({'name': new_name})
                #return {record.id:new_name}

    @api.depends('policy_id')
    def _get_default_priority(self):
        _logger.info('***** Entra a _get_default_priority *****')
        _logger.info('***** SELF: ' + str(self))
        record = self

        if record.policy_id:
            response = record.policy_id.default_priority
            record.write({'priority': response})
            return {record.id:response}

    @api.depends('policy_id')
    def _get_notified_emails(self):
        _logger.info('***** Entra a _get_notified_emails *****')
        record = self
        if record.policy_id:
            _logger.info('***** record.policy_id: ' + str(record.policy_id))
            emails_list = ','.join(record.policy_id.notified_uids.mapped('login'))
            partners_list = record.policy_id.notified_uids.mapped('partner_id')
            #_logger.info('***** partners_list: ' + str(partners_list.ids))
            #partners = self.env['res.partner'].search([('id', 'in', partners_list.ids)])
            _logger.info('***** emails_list: ' + str(emails_list))
            record.write({
                'notified_emails': emails_list,
                'notified_partner_ids': partners_list})
            #return {record.id: emails_list}

    @api.depends('show_form')
    def _get_authorization_form(self):
        _logger.info('***** Entra a _get_authorization_form: ' + str(self.new_vals))
        if self.show_form:
            _logger.info('***** Entra a _get_authorization_form con la política: ' + str(self.policy_id.name))
            _logger.info('***** model_id: ' + str(self.policy_id.model_id))
            _logger.info('***** res_id: ' + str(self.ids))
            _logger.info('***** policy_id: ' + str(self.policy_id.id))
            _logger.info('***** assigned_uid: ' + str(self.policy_id.authorizer_uid))
            _logger.info('***** new_vals: ' + str(self.new_vals))

            form = self.env.ref('mb_authorizations.view_authorization_task_form', False)
            action = {
                'name': 'New task',
                'type': 'ir.actions.act_window',
                'res_model': 'authorization.task',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(form.id, 'form')],
                'view_id': form.id,
                'context': {
                    'model_id': self.policy_id.model_id,
                    'res_id': self.ids,
                    'policy_id': self.policy_id.id,
                    'assigned_uid': self.policy_id.authorizer_uid,
                    'new_vals': str(self.new_vals)
                },
            }

            return action

    def _get_task_url(self):
        _logger.info('***** Entra a _get_task_url *****')
        _logger.info('***** SELF: ' + str(self))
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        _logger.info('***** base_url: ' + str(base_url))
        self.write({'task_url': base_url})
    
    name = fields.Char(compute='_get_default_name', store=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('authorized', 'Authorized'),
            ('rejected', 'Rejected')
        ], string='State', default='draft')
    priority = fields.Selection([
            ('0', 'Low'),
            ('1', 'Medium'),
            ('2', 'High'),
            ('3', 'Very High'),
        ], string='Priority', index=True, default=_get_default_priority)
    reason = fields.Text('Reason')
    model_id = fields.Many2one('ir.model', string='Model', required=True, related="policy_id.model_id")
    #model_id = fields.Char('Related Document Model', index=True)
    res_id = fields.Many2oneReference('Record', index=True, model_field='model_id', required=True)

    policy_id = fields.Many2one('authorization.policy', string='Authorization policy', required=True)
    applicant_uid = fields.Many2one('res.users', string='Applicant user', required=True)
    assigned_uid = fields.Many2one('res.users', string='Assigned user', required=True, related="policy_id.authorizer_uid")
    
    notified_emails = fields.Text(compute='_get_notified_emails', store=True)
    notified_partner_ids = fields.Many2many('res.partner', 'authorization_res_partner_needaction_rel', string='Partners with Need Action', compute='_get_notified_emails', store=True)

    task_url = fields.Char()

    new_vals = fields.Text(string='New values after authorize.')

    hide_button_authorize = fields.Boolean(compute="_hide_button_authorize", store=False)
    hide_task = fields.Boolean(compute="_hide_task", store=True)
    show_form = fields.Boolean()

    request_date = fields.Date()
    authorization_date = fields.Date()
    authorizer_uid = fields.Many2one('res.users', string='Authorizer')

    @api.model
    def create(self, vals):
        _logger.info('***** Entra a create de authorization.task *****')

        res = super(AuthorizationTask, self).create(vals)
        res._get_default_priority()
        res._get_task_url()
        #res.action_send_email()

        return res
        
    def _hide_button_authorize(self):
        _logger.info('***** Entra a _hide_button_authorize *****')
        for task in self:
            if self.env.uid == task.policy_id.authorizer_uid.id or self.env.uid in task.policy_id.notified_uids.ids:
                result = False
            else:
                result = True
            _logger.info('***** result: ' + str(result))
            task.sudo().hide_button_authorize = result
            task.sudo()._hide_task()

    def _hide_task(self):
        _logger.info('***** Entra a _hide_task *****')
        for task in self:
            _logger.info('***** task: ' + str(task))
            record = self.env[task.model_id.model].search([('id', '=', task.res_id)])
            if (task.model_id.model == 'res.partner' and (record.user_id == self.env.user or not record.user_id)) or task.model_id.model != 'res.partner':
                result = False
            else:
                result = True
            _logger.info('***** result: ' + str(result))
            task.sudo().hide_task = result

    def action_send_email(self):
        _logger.info('***** Entra a action_send_email *****')

        _logger.info('***** SELF: ' + str(self))

        if self.env.su:
            # sending mail in sudo was meant for it being sent from superuser
            self = self.with_user(SUPERUSER_ID)
        template_id = self.env['ir.model.data'].xmlid_to_res_id('mb_authorizations.authorization_assigned_notification_template', raise_if_not_found=False)
        if template_id:
            for task in self:
                if not task.reason:
                    raise UserError(_('Please specify a reason to authorize.'))

                # Para obtener la url de la tarea
                task._get_task_url()

                task.with_context(force_send=True).message_post_with_template(template_id, composition_mode='comment', email_layout_xmlid="mail.mail_notification_light", message_type='notification')
    
                task.write({'state': 'pending', 'request_date': datetime.today()})

                # Desasocia la autorozación del registro al que pertenece para que en dado caso se pueda crear otra
                related_record = self.env[task.model_id.model].search([('id', '=', task.res_id)])
                related_record.x_current_authorization_id = False

    def action_authorize(self):
        _logger.info('***** Entra a action_authorize *****')
        for task in self:
            _logger.info('***** Se autorizó, así que se actualizarán los datos: ' + str(task.new_vals))
            record = self.env[task.model_id.model].search([('id', '=', task.res_id)])
            record.write(eval(task.new_vals))
            task.write({'state': 'authorized','authorization_date': datetime.today(), 'authorizer_uid': self.env.uid})

            task.message_post(body=_('Authorized by ') + str(task.authorizer_uid.name) + '.')

    def action_reject(self):
        _logger.info('***** Entra a action_reject *****')
        for task in self:
            task.write({'state': 'rejected', 'authorization_date': datetime.today(), 'authorizer_uid': self.env.uid})

            task.message_post(body=_('Rejected by ') + str(task.authorizer_uid.name) + '.')