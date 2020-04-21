
from odoo import models, fields


class ResPartnerTestAnswer(models.Model):

    _name = 'res.partner.test.answer'
    _description = "Test answer sheet for partners"


    partner_id = fields.Many2one('res.partner', string = "Client", ondelete="cascade")
    question_id = fields.Many2one('res.partner.test.question', string = "Question", ondelete="cascade")
    option_id = fields.Many2one('res.partner.test.option', string = "Answer",
                                domain="[('question_id', '=', question_id)]")
    calculate_field = fields.Selection(selection = [('payment', 'Payment'),
                                                    ('purchase', 'Purchases')], related = 'question_id.calculate_field', store = True)
    sequence = fields.Integer(related = 'question_id.sequence', string = "Sequence")

