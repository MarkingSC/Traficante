
import logging
from odoo import models, fields, api, exceptions

_logger = logging.getLogger(__name__)

class ResPartnerTestQuestion(models.Model):

    _name = 'res.partner.test.question'
    _description = "Question for partner Purchases/Payment test"

    name = fields.Char(string = "Question")
    sequence = fields.Integer(string = "Sequence")
    calculate_field = fields.Selection(selection = [('payment', 'Payment'),
                                                    ('purchase', 'Purchases')], string = "Field", help = "Related test field")
    option_ids = fields.One2many('res.partner.test.option', inverse_name = 'question_id', string = "Options Available")

    @api.model
    def create(self, values):
        res = super(ResPartnerTestQuestion, self).create(values)
        if not 'option_ids' in values:
            raise exceptions.UserError("Options for question must be provided")
        partners = self.env['res.partner'].search([('customer_rank','>', 0)])
        for partner in partners:
            if res.calculate_field == 'payment':
                partner._get_payment_answer_ids()
            elif res.calculate_field == 'purchase':
                partner._get_purchase_answer_ids()
        return res


class ResPartnerTestOption(models.Model):

    _name = 'res.partner.test.option'
    _description = "Selectable options for test questions"

    name = fields.Char(string = "Label")
    question_id = fields.Many2one('res.partner.test.question', string = "Question",
                                  help = "Question which this option belongs to", ondelete='cascade')
    points = fields.Integer(string = "Points")
    sequence = fields.Integer(string = "Sequence")
    #type = fields.Selection(selection = [('range', 'Range'),
    #                                     ('value', 'Value')], string = "Type")
    #range_sup_limit = fields.Float(string = "Superior limit")
    #range_inf_limit = fields.Float(string="Inferior limit")
    #value = fields.Float(string = "Value")
