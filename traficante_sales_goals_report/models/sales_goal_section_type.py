
from email.policy import default
import logging
from odoo import models, fields, api, _, exceptions
import odoo
from datetime import timedelta, datetime

datetime.today()

_logger = logging.getLogger(__name__)

class SalesGoalSectionType(models.Model):
    _name = 'sales.goal.section.type'
    _description = 'Section type for goals'

    name = fields.Char(string='Name', required=True, help='Set the name of the section')

    # si se muestra el nombre en el encabezado
    show_name = fields.Boolean(default=True, help="Set active to false to hide the name as header on the sales report.")
    # Si se muestra el porcentaje de la meta en el encabezado
    show_goal_pct = fields.Boolean(default=True, help="Set active to false to hide goal percentages on header.")
    # Si se muestra el monto de la venta en el encabezado
    show_sales_amount = fields.Boolean(default=True, help="Set active to false to hide sales amount on header.")
    # Si se muestra el total de la venta en el footer
    show_total = fields.Boolean(default=True, help="Set active to false to hide the total amount as footer on the sales report.")

    total_row_name = fields.Char(string='Total row name', help='Text to display on total row.')

    bg_color = fields.Char(string='Background color', help='Set the color for background on report.', default='#ffffff')
    font_color = fields.Char(string='Font color', help='Set the font color on report.', default='#000000')

    

