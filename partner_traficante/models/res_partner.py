
import logging
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
                                                                       ('id', 'not in', [partner_question_ids.id])],
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
        _logger.debug('//////partner_purchase_answer_ids//////')
        _logger.debug(partner_purchase_answer_ids)
        partner_question_ids = partner_purchase_answer_ids.mapped('question_id')
        _logger.debug('//////partner_question_ids//////')
        _logger.debug(partner_question_ids)
        questions_left = self.env['res.partner.test.question'].search([('calculate_field', '=', 'purchase'),
                                                                       ('id', 'not in', [partner_question_ids.id])],
                                                                      order = 'sequence')
        _logger.debug('//////questions_left//////')
        _logger.debug(questions_left)
        new_answers = []
        for question in questions_left:
            new_answer = self.env['res.partner.test.answer'].create({
                'partner_id': self.id,
                'question_id': question.id,
                'calculate_field': question.calculate_field})
            new_answers.append(new_answer.id)
        _logger.debug('//////new_answers//////')
        _logger.debug(new_answers)
        return new_answers

    @api.onchange('payment_answer_ids')
    def _set_payment_test_result(self):
        sum_points = 0
        for answer in self.payment_answer_ids:
            if answer.option_id and answer.option_id.points > 0 and sum_points >= 0:
                sum_points += answer.option_id.points
                _logger.debug('//////sum_points good/////')
                _logger.debug(sum_points)
            elif answer.option_id and answer.option_id.points < 0:
                sum_points = -1
                _logger.debug('//////sum_points bad/////')
                _logger.debug(sum_points)
        _logger.debug('//////sum_points/////')
        _logger.debug(sum_points)
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

    # Fields to solve 1.1 phase
    purchase_test_result = fields.Many2one('res.partner.test.result', string = "Purchases")
    payment_test_result = fields.Many2one('res.partner.test.result', string = "Payment")
    pmf = fields.Float(string="Monthly invoice amount avg")
    pmfxp = fields.Float(string="Monthly invoice amount avg p/person")
    capacity = fields.Integer(string="Capacity")
    is_distributor = fields.Boolean(string="Is distributor", default=False)
    category_id = fields.Many2one('res.partner.category', string="Category")
    size_id = fields.Many2one('res.partner.size', string="Size")
    payment_answer_ids = fields.One2many('res.partner.test.answer', inverse_name='partner_id', default = _get_payment_answer_ids,
                                         domain=[('calculate_field', '=', 'payment')], string = "Answer the questions")
    purchase_answer_ids = fields.One2many('res.partner.test.answer', inverse_name='partner_id', default = _get_purchase_answer_ids,
                                          domain=[('calculate_field', '=', 'purchase')], string = "Answer the questions")


