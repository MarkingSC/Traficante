
import logging
from odoo import models, fields, api, _, exceptions
import odoo
from datetime import timedelta, datetime
import pytz
from odoo.exceptions import AccessError, UserError, ValidationError

datetime.today()

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('partner_id')
    def get_delivery_times(self):
        for move in self:
            start = '{0:02.0f}:{1:02.0f}'.format(*divmod(move.partner_id.start_delivery_time * 60, 60))
            finish = '{0:02.0f}:{1:02.0f}'.format(*divmod(move.partner_id.finish_delivery_time * 60, 60))
            move.partner_delivery_time = start + ' - ' + finish

    @api.depends('partner_id')
    def get_delivery_address(self):
        for move in self:
            partner = move.partner_id
            addressList = [partner.street,
                        partner.street2,
                        partner.city,
                        partner.state_id.name,
                        partner.country_id.name]

            move.partner_address = ",".join(map(str, addressList))

    on_delivery_route = fields.Boolean(string="On delivery route", default = False)
    partner_delivery_time = fields.Char(string="Customer receiving times", readonly=True, compute=get_delivery_times)
    partner_zone_id = fields.Many2one('res.partner.zone', string="Customer zone", related='partner_id.zone_id', readonly=True)
    partner_address =fields.Char(string="Delivery address", compute=get_delivery_address)
    partner_business_name = fields.Char(string="Business name", store=True, related='partner_id.business_name')
    partner_zip_code = fields.Char(string="Business name", store=True, related='partner_id.zip')

    @api.depends('origin', 'invoice_ids')
    def get_invoices_amount(self):
        _logger.info("**** INICIA get_invoices_amount")
        for move in self:
            if move.origin:
                _logger.info("str(self.invoice_ids): " + str(move.invoice_ids))
                _logger.info("str(self.invoice_ids.mapped('amount_total')): " + str(move.invoice_ids.mapped('amount_total')))
                _logger.info("','.join(['1','2','3']): " + ','.join(['1','2','3']))
                #_logger.info("','.join(['1','2','3']): " + ','.join([1,2,3]))
                move.invoice_amounts = str(",".join(move.invoice_ids.mapped(lambda r: "${:,.2f}".format(r.amount_total))))
            else:
                move.invoice_amounts = ''

    def get_invoices(self):
        for move in self:
            if move.origin:
                move.invoice_ids = self.env['account.move'].search([('invoice_origin', '=', move.origin)]).ids
            else:
                move.invoice_ids = []

    invoice_ids = fields.Many2many('account.move', ondelete='restrict', string='invoices', compute=get_invoices)
    invoice_amounts = fields.Char(string="Invoices amount", compute=get_invoices_amount)

    def button_validate(self):
        # Evalúa si hay facturas validadas para la validación del movimiento
        _logger.info("**** INICIA button_validate")
        _logger.info("**** INICIA self.invoice_ids: " + str(self.invoice_ids))
        _logger.info("**** INICIA self.picking_type_code: " + str(self.picking_type_code))
        _logger.info("**** INICIA self.origin: " + str(self.origin))

        postedInvoices = self.invoice_ids.filtered(lambda r: r.state == 'posted')

        if self.picking_type_code == 'outgoing' and self.origin:
            if len(postedInvoices)  == 0:
                raise UserError("No es posible validar el movimiento. No existen facturas confirmadas para este pedido.")

            if self.on_delivery_route != True:
                raise UserError("No es posible validar el movimiento. Esta entrega debe estar programada en ruta para continuar.")

        return super(StockPicking, self).button_validate()

    def action_set_delivery_route_date(self):
        _logger.info("**** INICIA action_set_delivery_route_date")  
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

    @api.model
    def action_set_delivery_route_date_form(self, vals):
        
        _logger.info("**** INICIA action_set_delivery_route_date_form")  
        _logger.info("self.env.ref('stock_traficante.stock_picking_delivery_route_date_multi').id: " + str(self.env.ref('stock_traficante.stock_picking_delivery_route_date_multi').id))  
        _logger.info("**** self.env.context: " + str(self.env.context)) 
        _logger.info("**** vals: " + str(vals))  

        data = dict()
        data['active_ids'] = vals

        return {
            'name': _('Set delivery route date'),
            'res_model': 'stock.picking.route.register',
            'view_mode': 'form',
            'view_id': self.env.ref('stock_traficante.stock_picking_delivery_route_date_multi').id,
            'context': data,
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
        _logger.info("**** INICIA default_get")  
        if not self.env.user.tz:
            raise exceptions.UserError("Es necesario establecer una zona horaria desde las preferencias su usuario.")
        tz = pytz.timezone(str(self.env.user.tz))

        rec = super(pickingRouteRegister, self).default_get(fields)

        rec['scheduled_date'] = tz.fromutc(odoo.fields.Datetime.now()).date() + timedelta(days=1)

        _logger.info("***** self._context: " + str(self._context)) 
        _logger.info("***** self.env.context: " + str(self.env.context)) 

        '''
        if self._context.get('params'):            
            _logger.info("***** self._context.get('params').get('id'): " + str (self._context.get('params').get('id')))  
            active_ids = self._context.get('params').get('id')
        else:
            _logger.info("***** self._context.get('active_ids'): " + str(self._context.get('active_ids')))  
            active_ids = self._context.get('active_ids')
        '''
        active_ids = self._context.get('active_ids')
        
        if not active_ids:
            return rec
        moves = self.env['stock.picking'].browse(active_ids)

        _logger.info("***** moves: " + str(moves))  

        # check if moves are in right state
        if any(move.state != 'assigned' for
               move in moves):
            raise exceptions.UserError("Solo pueden salir a ruta pedidos preparados.")

        if 'stock_picking_ids' not in rec:
            rec['stock_picking_ids'] = [(6, 0, moves.ids)]
        return rec

    def add_to_route(self):
        _logger.info("**** INICIA add_to_route")  
        tz = pytz.timezone(str(self.env.user.tz))
        utc_now = fields.Datetime.now()
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
