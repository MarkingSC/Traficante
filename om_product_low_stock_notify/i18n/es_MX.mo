��    .      �  =   �      �  |  �  G   n  s   �     *  	   0     :     B  
   R  
   ]     h     u     �     �     �     �     �  
   �     �     �     �     �               4     L     b     s     �  	   �     �  
   �     �  %   �          	       ,   :     g     x     �     �     �     �  	   �     �  "  �  6  �  h   *&  �   �&     P'     W'  
   c'     n'  
   �'     �'     �'     �'     �'     �'     �'     �'     �'  
   �'     (     (     7(  
   N(      Y(  $   z(  $   �(     �(     �(     �(     )     #)     /)     ?)  !   K)  9   m)     �)      �)  $   �)  7   �)     .*     D*     X*     l*     s*     �*     �*     �*        .      ,         '       "                  !                            
           )      *         #   %      (             &                                   +             $                 	      -       
                    <table border="0" width="100%" cellpadding="0" bgcolor="#ededed" style="padding: 20px; background-color: #ededed; border-collapse:separate;" summary="o_mail_notification">
                        <tbody>
                          <tr>
                            <td align="center" style="min-width: 590px;">
                              <table width="590" border="0" cellpadding="0" bgcolor="#875A7B" style="min-width: 590px; background-color:#3482a8; padding: 20px; border-collapse:separate;">
                                <tr>
                                  <td valign="middle">
                                      <span style="font-size:20px; color:white; font-weight: bold;">
                                          Product Low Stock
                                      </span>
                                  </td>
                                  <td valign="middle" align="right">
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>

                          <!-- CONTENT -->
                          <tr>
                            <td align="center" style="min-width: 590px;">
                              <table width="590" border="0" cellpadding="0" bgcolor="#ffffff" style="min-width: 590px; background-color: rgb(255, 255, 255); padding: 20px; border-collapse:separate;">
                                <tbody>
                                  <td valign="top" style="font-family:Arial,Helvetica,sans-serif; color: #555; font-size: 14px;">
                                    <p>Hello ,
                                    <p>Please find attached report for the list of products whose quantity is lower then the minimum quantity.</p>
                                  </td>
                                </tbody>
                              </table>
                            </td>
                          </tr>
                          <tr>
                            <td align="center" style="min-width: 590px;">
                              <table width="590" border="0" cellpadding="0" bgcolor="#875A7B" style="min-width: 590px; background-color:#3482a8; padding: 20px; border-collapse:separate;">
                                <tr>
                                  <td valign="middle" align="left" style="color: #fff; padding-top: 10px; padding-bottom: 10px; font-size: 12px;">
                                    ${object.company_id.name}<br/>
                                    ${object.company_id.phone or ''}
                                  </td>
                                  <td valign="middle" align="right" style="color: #fff; padding-top: 10px; padding-bottom: 10px; font-size: 12px;">
                                    % if object.company_id.email:
                                    <a href="mailto:${object.company_id.email}" style="text-decoration:none; color: white;">${object.company_id.email}</a><br/>
                                    % endif
                                    % if object.company_id.website:
                                        <a href="${object.company_id.website}" style="text-decoration:none; color: white;">
                                            ${object.company_id .website}
                                        </a>
                                    % endif
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </tbody>
                    </table>
                
             ${(object.company_id.name or '').replace('/','_')+ 'Product Low Stock'} <span title="Values set here are company-specific." role="img" aria-label="Values set here are company-specific."/> Close Companies Company Config Settings Created by Created on Display Name Filter By Location Filter By Warehouse Forecast Forecast Quantity Global ID Individual Last Modified on Last Updated by Last Updated on Location Low Stock Nofitication Low Stock Notification Low Stock Notification? Min Quantity Based on Minimum Quantity Minimum Quantity Based On Notification Based on Notify To On Hand Quantity PDF Report PRODUCT LOW STOCK Please Add Users in Send Notification Product Product Low Stock Product Low Stock Notification Product Low Stock Notification Configration. Product Template Quantity Limit Record Rules Send Send Nofitication Send Notification Email Warehouse or Project-Id-Version: Odoo Server 13.0-20220126
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2022-05-31 14:51-0500
Last-Translator: 
Language-Team: 
Language: es_MX
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: 
X-Generator: Poedit 3.0.1
 
                    <table border=“0” width=“100%” cellpadding=“0” bgcolor=“#ededed” style=“padding: 20px; background-color: #ededed; border-collapse:separate;” summary=“o_mail_notification”>
                        <tbody>
                          <tr>
                            <td align=“center” style=“min-width: 590px;”>
                              <table width=“590” border=“0” cellpadding=“0” bgcolor=“#875A7B” style=“min-width: 590px; background-color:#3482a8; padding: 20px; border-collapse:separate;”>
                                <tr>
                                  <td valign=“middle”>
                                      <span style=“font-size:20px; color:white; font-weight: bold;”>
                                          Productos con baja disponibilidad
                                      </span>
                                  </td>
                                  <td valign=“middle” align=“right”>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>

                          <!— CONTENT —>
                          <tr>
                            <td align=“center” style=“min-width: 590px;”>
                              <table width=“590” border=“0” cellpadding=“0” bgcolor=“#ffffff” style=“min-width: 590px; background-color: rgb(255, 255, 255); padding: 20px; border-collapse:separate;”>
                                <tbody>
                                  <td valign=“top” style=“font-family:Arial,Helvetica,sans-serif; color: #555; font-size: 14px;”>
                                    <p>Hola ,
                                    <p>Adjunto encontrará el reporte de productos cuya disponibilidad es menor al mínimo establecido.</p>
                                  </td>
                                </tbody>
                              </table>
                            </td>
                          </tr>
                          <tr>
                            <td align=“center” style=“min-width: 590px;”>
                              <table width=“590” border=“0” cellpadding=“0” bgcolor=“#875A7B” style=“min-width: 590px; background-color:#3482a8; padding: 20px; border-collapse:separate;”>
                                <tr>
                                  <td valign=“middle” align=“left” style=“color: #fff; padding-top: 10px; padding-bottom: 10px; font-size: 12px;”>
                                    ${object.company_id.name}<br/>
                                    ${object.company_id.phone or ‘’}
                                  </td>
                                  <td valign=“middle” align=“right” style=“color: #fff; padding-top: 10px; padding-bottom: 10px; font-size: 12px;”>
                                    % if object.company_id.email:
                                    <a href=“mailto:${object.company_id.email}” style=“text-decoration:none; color: white;”>${object.company_id.email}</a><br/>
                                    % endif
                                    % if object.company_id.website:
                                        <a href=“${object.company_id.website}” style=“text-decoration:none; color: white;”>
                                            ${object.company_id .website}
                                        </a>
                                    % endif
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </tbody>
                    </table>
                
             ${(object.company_id.name or ‘’).replace(‘/‘,’_’)+ ‘Productos con baja disponibilidad ’} <span title=“Los valores establecidos aquí son específicos para las compañías.” role=“img” aria-label=“Los valores establecidos aquí son específicos para las compañías./> Cerrar Compañías Compañía Opciones de Configuración Creado por Creado Nombre mostrado Filtrar por ubicación Filtrar por almacén Previsto Cantidad prevista Global ID Individual Última modificación Última modificación por Última actualización Ubicación Notificación de inventario bajo Notificación de baja disponibilidad Notificación de baja disponibilidad Cantidad mínima basada en Cantidad mínima Cantidad mínima basada en Notificación basada en Notificar a Cantidad a mano Reporte PDF PRODUCTOS CON BAJA DISPONIBILIDAD Por favor agregue usuarios en el envío de notificaciones Producto Producto con baja disponibilidad Notificación de baja disponibilidad Configuración de notificaciones de baja disponibilidad Plantilla de producto Límite de cantidad Reglas del registro Enviar Enviar notificación Enviar notificación por correo Almacén O 