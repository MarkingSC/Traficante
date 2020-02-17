
import logging
from odoo import models, fields, api, _, exceptions
import odoo
from datetime import timedelta, datetime
import pytz

datetime.today()

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('partner_id')
    def get_delivery_times(self):
        start = '{0:02.0f}:{1:02.0f}'.format(*divmod(self.partner_id.start_delivery_time * 60, 60))
        finish = '{0:02.0f}:{1:02.0f}'.format(*divmod(self.partner_id.finish_delivery_time * 60, 60))
        self.partner_delivery_time = start + ' - ' + finish

    on_delivery_route = fields.Boolean(string="On delivery route", default = False)
    partner_delivery_time = fields.Char(String="Customer receiving times", readonly=True, compute=get_delivery_times)
    partner_zone_id = fields.Many2one('res.partner.zone', String="Customer zone", related='partner_id.zone_id', readonly=True)

    def get_invoices(self):
        for move in self:
            if move.origin:
                move.invoice_ids = self.env['account.move'].search([('invoice_origin', '=', move.origin)]).ids
            else:
                move.invoice_ids = []

    invoice_ids = fields.Many2many('account.move', ondelete='restrict', string='invoices', compute=get_invoices)

    def action_set_delivery_route_date(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        return {
            'name': _('Set delivery route date'),
            'res_model': 'stock.picking.route.register',
            'view_mode': 'form',
            'view_id': self.env.ref('stock_traficante.stock_picking_delivery_route_date_multi').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

class pickingRouteRegister(models.TransientModel):
    _name = 'stock.picking.route.register'
    _description = 'Set route date'

    scheduled_date = fields.Date(required=True)
    stock_picking_ids = fields.Many2many("stock.picking",
                                         "stock_picking_route_register_rel_transient",
                                         "date_setting_id","invoice_id",
                                         string="Stock moves", copy=False, readonly=True)


    @api.model
    def default_get(self, fields):
        if not self.env.user.tz:
            raise exceptions.UserError("Es necesario establecer una zona horaria desde las preferencias su usuario.")
        tz = pytz.timezone(str(self.env.user.tz))

        rec = super(pickingRouteRegister, self).default_get(fields)

        rec['scheduled_date'] = tz.fromutc(odoo.fields.Datetime.now()).date() + timedelta(days=1)

        active_ids = self._context.get('active_ids')
        if not active_ids:
            return rec
        moves = self.env['stock.picking'].browse(active_ids)

        for move in moves:
            _logger.debug('elemento: ' + move.state)
            if move.invoice_ids.filtered(lambda r: r.invoice_payment_state == 'paid'):
                continue
            else:
                raise exceptions.UserError("Solo pueden salir a ruta pedidos con facturas pagadas.")

        # check if moves are in right state
        if any(move.state != 'assigned' for
               move in moves):
            raise exceptions.UserError("Solo pueden salir a ruta pedidos preparados.")

        if 'stock_picking_ids' not in rec:
            rec['stock_picking_ids'] = [(6, 0, moves.ids)]
        return rec

    def add_to_route(self):
        tz = pytz.timezone(str(self.env.user.tz))
        utc_now = fields.Datetime.now();
        now_user = tz.fromutc(fields.Datetime.now()).replace(tzinfo=None)
        diferencia = utc_now - now_user
        fecha_res = datetime.combine(self.scheduled_date, datetime.min.time()) + diferencia

        for record in self.stock_picking_ids:
            record.write({
                'on_delivery_route': True,
                'scheduled_date': fecha_res})

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
