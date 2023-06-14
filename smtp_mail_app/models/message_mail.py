from odoo import api, fields, models


class MailMessage(models.Model):
    _inherit = "mail.message"


    company_ids = fields.Many2one("res.company", "Company Name")

   
    @api.model_create_multi
    def create(self, vals):
        for mail in vals:
            if mail.get("model") and mail.get("res_id"):
                current_object = self.env[mail["model"]].browse(mail["res_id"])
                if hasattr(current_object, "company_ids") and current_object.company_id:
                    mail["company_ids"] = current_object.company_id.id
            if not mail.get("company_ids"):
                mail["company_ids"] = self.env.company.id
            if not mail.get("mail_server_id"):
                mail["mail_server_id"] = (self.sudo().env["ir.mail_server"].search([("company_ids", "=", mail.get("company_ids", False))],order="sequence",limit=1,).id)
        return super(MailMessage, self).create(mail)