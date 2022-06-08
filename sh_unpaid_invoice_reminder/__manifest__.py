# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Unpaid Invoice Auto Email",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "category": "Accounting",

    "summary": """
unpaid invoice reminder module, unpaid payment automatic mail,
unpaid invoice notifier app, unpaid payment alert odoo
""",
    "description": """
This module is useful to send a reminder to the customer for unpaid invoices.
Here you can send email notification for an unpaid invoice.
Easy to set unpaid invoices due day reminders before/after days.
for example, you can send reminders to the customer
before 3 days of the due date of the invoice.
You can easily create a reminder as you want.
You can set a reminder as a manually or using a cron job.
You can see reminder history as well in the mail.
After enable "Don"t Send Unpaid Email Notification" you can stop
sending an email of the unpaid invoice to the particular customer.
""",

    "version": "13.0.4",

    "depends": ['account'],

    "data": [
        'security/ir.model.access.csv',
        'data/unpaid_invoice_reminder.xml',
        'data/template_account_unpaid_invoice_reminder_email.xml',
        'views/unpaid_remainder.xml',
        'views/res_config_setting.xml',
        'views/account_move.xml',
        'views/account_unpaid_invoice_reminder.xml',
    ],

    "images": ['static/description/background.png', ],
    "live_test_url": "https://youtu.be/bdbQth64I7Q",
    "auto_install": False,
    "application": True,
    "installable": True,
    "price": 20,
    "currency": "EUR"
}
