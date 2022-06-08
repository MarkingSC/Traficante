��    "      ,  /   <      �  F   �  �  @  	   �     �            
     
   )     4  $   A     f     o     �     �     �     �     �     �     �     �     �  	   �            +   !     M     ^     l  3   �     �     �  %   �     	  "  	  I   6
  �  �
     Q     ]     x     �  
   �  	   �     �     �     �     �                    (     H     [     q     �     �     �     �     �  6   �          5  %   M  O   s     �  "   �  4   �     /                                  	                            
                                                       !                                  "       ${object.company_id.name} Unpaid Invoice (Ref ${object.name or 'n/a'}) <div>
<p>Dear ${object.partner_id.name}
% set access_action = object.with_context(force_website=True).get_access_action()
% set is_online = access_action and access_action['type'] == 'ir.actions.act_url'

% if object.partner_id.parent_id:
    (<i>${object.partner_id.parent_id.name}</i>)
% endif
,</p>
        <br/><br/>
<p>Here is, in attachment, your 
% if object.name:
invoice <strong>${object.name}</strong>
% else:
invoice
% endif
% if object.origin:
(with reference: ${object.origin})
% endif
amounting in <strong>${object.amount_total} ${object.currency_id.name}</strong>
from ${object.company_id.name}.
</p>

    <br/><br/>

% if object.state=='posted':
    <p>This invoice is already posted.</p>
% else:
    <p>Please remit payment at your earliest convenience.</p>
% endif

<p>Thank you,</p>
<p style="color:#888888">
% if object.user_id and object.user_id.signature:
    ${object.user_id.signature | safe}
% endif
</p>
</div> Companies Config Settings Configure Reminder Contact Created by Created on Display Name Don't Send Unpaid Email Notification Due Date Email Notification ? ID Invoice Invoice Date Invoice Due Reminder Journal Entries Last Modified on Last Updated by Last Updated on Mail Mail Date Notification? Remainder History Reminder Days Before/After (Days)-(+ve/-ve) Reminder History Reminder Name Send Email Notification on Send Email Notification on Invoice Date OR Due Date Template Unpaid Invoice Reminder Unpaid Invoice Reminder Configuration Unpaid Remainder Project-Id-Version: Odoo Server 13.0-20211018
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2022-06-07 09:11-0500
Last-Translator: 
Language-Team: 
Language: es_MX
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: 
X-Generator: Poedit 3.0.1
 ${object.company_id.name} Factura sin pagar (Ref ${object.name or 'n/a'}) <div>
<p> Estimado(a) ${object.partner_id.name}
% set access_action = object.with_context(force_website=True).get_access_action()
% set is_online = access_action and access_action['type'] == 'ir.actions.act_url'

% if object.partner_id.parent_id:
    (<i>${object.partner_id.parent_id.name}</i>)
% endif
,</p>
        <br/><br/>
<p>Encontrará en los adjuntos su 
% if object.name:
factura <strong>${object.name}</strong>
% else:
factura
% endif
% if object.origin:
(referencia: ${object.origin})
% endif
por un total de <strong>${object.amount_total} ${object.currency_id.name}</strong>
de ${object.company_id.name}.
</p>

    <br/><br/>

% if object.state=='posted':
    <p>Por favor efectúe su pago tan pronto como le sea posible.</p>
% else:
    <p>Por favor efectúe su pago tan pronto como le sea posible.</p>
% endif

<p>Gracias,</p>
<p style="color:#888888">
% if object.user_id and object.user_id.signature:
    ${object.user_id.signature | safe}
% endif
</p>
</div> Compañías Opciones de Configuración Configurar recordatorio Contacto Creado por Creado en Nombre mostrado No enviar recordatorios de pago Fecha compromiso Enviar recordatorios de pago ID Factura Fecha de factura Recordatorio de pago de factura Asientos contables Última modificación Última actualización por Última actualización Correo Fecha de correo Notificación Historial de recordatorios Días de recordatorio Antes/Después (Días)-(+ve/-ve) Historial de recordatorios Nombre del recordatorio Enviar notificación por correo sobre Enviar notificación por correo sobre la fecha de factura o la fecha compromiso Plantilla de correo Recordatorio de facturas sin pagar Configuración de recordatorio de facturas sin pagar Unpaid Invoice Reminder 