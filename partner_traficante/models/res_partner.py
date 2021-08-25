
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


_logger = logging.getLogger(__name__)
class ResPartner(models.Model):

    _inherit = 'res.partner'

    zone_id = fields.Many2one('res.partner.zone', string='Zone')
    start_delivery_time = fields.Float(string="Start delivery time")
    finish_delivery_time = fields.Float(string="Finish delivery time")
    default_journal_id = fields.Many2one('account.journal', string='Journal', required=False, readonly=False,
                                        tracking=True,
                                        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]")


    def _get_payment_answer_ids(self):

        partner_payment_answer_ids = self.payment_answer_ids

        partner_question_ids = partner_payment_answer_ids.mapped('question_id')
        questions_left = self.env['res.partner.test.question'].search([('calculate_field', '=', 'payment'),
                                                                       ('id', 'not in', partner_question_ids.mapped('id'))],
                                                                      order = 'sequence')
        new_answers = []
        for question in questions_left:
            new_answer = self.env['res.partner.test.answer'].create({
                'partner_id': self.id,
                'question_id': question.id,
                'calculate_field': question.calculate_field})
            new_answers.append(new_answer.id)
        return new_answers

    def _get_purchase_answer_ids(self):

        partner_purchase_answer_ids = self.purchase_answer_ids
        partner_question_ids = partner_purchase_answer_ids.mapped('question_id')
        questions_left = self.env['res.partner.test.question'].search([('calculate_field', '=', 'purchase'),
                                                                       ('id', 'not in', partner_question_ids.mapped('id'))],
                                                                      order = 'sequence')
        new_answers = []
        for question in questions_left:
            new_answer = self.env['res.partner.test.answer'].create({
                'partner_id': self.id,
                'question_id': question.id,
                'calculate_field': question.calculate_field})
            new_answers.append(new_answer.id)
        return new_answers


    @api.onchange('capacity')
    def _get_pmfxp(self):
        for client in self:
            average_xp = 0
            if client.capacity:
                average_xp = client.pmf / client.capacity
            client.write({
                'pmfxp': average_xp
            })


    @api.onchange('payment_answer_ids')
    def _set_payment_test_result(self):
        sum_points = 0
        for answer in self.payment_answer_ids:
            if answer.option_id and answer.option_id.points > 0 and sum_points >= 0:
                sum_points += answer.option_id.points
            elif answer.option_id and answer.option_id.points < 0:
                sum_points = -1
        self.payment_test_result = self.env['res.partner.test.result'].search([
            ('res_field', '=', 'payment'),
            ('sup_limit', '>=', sum_points),
            ('inf_limit', '<=', sum_points)], limit=1)

    @api.onchange('purchase_answer_ids')
    def _set_purchase_test_result(self):
        sum_points = 0
        for answer in self.purchase_answer_ids:
            if answer.option_id and answer.option_id.points > 0 and sum_points >= 0:
                sum_points += answer.option_id.points
            elif answer.option_id and answer.option_id.points < 0:
                sum_points = -1
        self.purchase_test_result = self.env['res.partner.test.result'].search([
            ('res_field', '=', 'purchase'),
            ('sup_limit', '>=', sum_points),
            ('inf_limit', '<=', sum_points)], limit=1)

    @api.onchange('capacity', 'est_category_id')
    def _onchange_get_est_size(self):
        self.size_id = self.env['res.partner.size'].search([
            ('est_category_id', '=', self.est_category_id.id),
            ('sup_limit', '>=', self.capacity),
            ('inf_limit', '<=', self.capacity)], limit=1)



    # Fields to solve 1.1 phase
    purchase_test_result = fields.Many2one('res.partner.test.result', string = "Purchases")
    payment_test_result = fields.Many2one('res.partner.test.result', string = "Payment")
    pmf = fields.Float(string="Monthly invoiced amount avg")
    pmfxp = fields.Float(string="Monthly invoiced amount avg p/person")
    capacity = fields.Integer(string="Capacity")
    is_distributor = fields.Boolean(string="Is distributor", default=False)
    est_category_id = fields.Many2one('res.partner.establishment.category', string="Category")
    size_id = fields.Many2one('res.partner.size', string="Size")
    payment_answer_ids = fields.One2many('res.partner.test.answer', inverse_name='partner_id', default = _get_payment_answer_ids,
                                         domain=[('calculate_field', '=', 'payment')], string = "Answer the questions")
    purchase_answer_ids = fields.One2many('res.partner.test.answer', inverse_name='partner_id', default = _get_purchase_answer_ids,
                                          domain=[('calculate_field', '=', 'purchase')], string = "Answer the questions")
    invoice_avg_ids = fields.One2many('account.invoice.avg', inverse_name='partner_id')


    # Campos para resolver requerimientos de fase 2.1
    customer_type = fields.Selection(selection = [('P','Prospecto'),('A','Activo')], string='Tipo', default="P", required=True)
    establishment_status=fields.Selection(selection = [('A','Abierto'),('C','Cerrado')], string='Estado de Establecimiento', default="A")