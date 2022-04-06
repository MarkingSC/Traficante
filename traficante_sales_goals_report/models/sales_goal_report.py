from odoo import models


class AccountTaxReport(models.TransientModel):
    _inherit = "account.common.report"
    _name = 'sales.goal.report'
    _description = 'Sales Goal Report'

    def _print_report(self, data):
        return self.env.ref(
            'traficante_sales_goals_report.action_report_sales_goals').report_action(
            self, data=data)
