
import logging
from odoo import models, fields, api, exceptions, _, SUPERUSER_ID


_logger = logging.getLogger(__name__)

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        return super(SaleAdvancePaymentInv, self.with_user(SUPERUSER_ID)).create_invoices()