
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
    customer_type = fields.Selection(selection = [('P','Prospecto'),('A','Activo'),('X','Suspendido')], string='Tipo', default="P", required=True)
    establishment_status=fields.Selection(selection = [('A','Abierto'),('C','Cerrado')], string='Estado del Establecimiento', default="A")

    # Función que cambia la segmentación del cliente y le resetea los valores de credito, ventas, compras y evaluaciones
    def _update_customer_type_from_orders(self):

        _logger.info("**** INICIA _update_customer_type_from_orders")

        last_order = self.env['sale.order'].search([('partner_id', '=', self.id)], limit = 1, order ='date_order desc')
        today_date = datetime.today()
        total_due = None

        try:
            _logger.info('**** self.total_due: ' + str(self.total_due))
            total_due = self.total_due
        except:
            _logger.info('**** No se pudo obtener self.total_due ')
            total_due = 0

        if (not last_order.date_order) and total_due <= 0:
            # Si no tiene ventas y no debe nada
            _logger.info('**** entra a if not last_order.date_order: ')
            _logger.info("**** Cambia el segmento del cliente y reinicia los valores de evaluación de cliente")
            self.write({
                'customer_type': 'X', 
                'pmf': '0',
                'pmfxp': '0',
                'active_limit': False,
                'warning_stage': '0',
                'blocking_stage': '0',
                'payment_test_result': None,
                'purchase_test_result': None})
            self.payment_answer_ids.write({'option_id': None})
            self.purchase_answer_ids.write({'option_id': None})
        elif last_order.date_order:
            # Si si tiene ventas, evalua la fecha de la ultima venta
            _logger.info('**** entra a ELSE de if not last_order.date_order: ')
            if ((today_date - last_order.date_order).days/30.4) > 3 and total_due <= 0:
                _logger.info("**** Cambia el segmento del cliente y reinicia los valores de evaluación de cliente")
                self.write({
                    'customer_type': 'X', 
                    'pmf': '0',
                    'pmfxp': '0',
                    'active_limit': False,
                    'warning_stage': '0',
                    'blocking_stage': '0',
                    'payment_test_result': None,
                    'purchase_test_result': None})
                self.payment_answer_ids.write({'option_id': None})
                self.purchase_answer_ids.write({'option_id': None})
            else:
                self.write({'customer_type': 'A'})
        

        _logger.info("**** TERMINA _update_customer_type_from_orders")
        return True

    @api.depends('is_company', 'name', 'parent_id.display_name', 'type', 'company_name')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None, html_format=None, show_vat=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            if not partner.business_name:
                partner.display_name = names.get(partner.id)
            else:
                partner.display_name = names.get(partner.id) + ' | ' + partner.business_name


