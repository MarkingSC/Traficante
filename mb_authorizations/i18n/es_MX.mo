��    o      �  �         `	  �  a	     �               #     /  
   B     M     k     z     �  	   �     �     �     �     �     �     �               &     =     R     e     y     �     �     �     �  	   �  
   �  
             !  
   /  
   :     E     X     l     }     �  	   �     �     �     �     �  	   �     �     �  '   �  0     0   P     �     �     �     �     �     �     �     �     �     �     �                    1     H     ^     q     �     �     �  +   �  &   �          &     -     G  %   O     u     ~     �     �  
   �     �     �     �     �     �     �  	   �  �   �  x   v     �  x   �     n     w     }     �  	   �  "   �  )   �     	       	   1     ;     P     c     k     q  �  �           7     M     a     r     ~  &   �     �     �     �     �     �          *     B     P     `     n     �     �     �     �     �  )   
     4     R     a     |  	   �  
   �     �     �     �  
   �  	   �     �     �          .     >  
   G     R     g     }     �     �     �     �  /   �  =   �  >   0      o      ~      �      �      �      �      �      �      �      �      �      !     !  $   !     @!  !   ]!     !     �!     �!     �!     �!  -   �!  '    "     H"     f"     m"  	   �"  -   �"  
   �"  	   �"  	   �"     �"     �"     �"     #  	   #     #     (#     <#     O#  �   b#  �   �#     �$  |   �$     "%     6%     B%     V%     f%      o%  +   �%     �%     �%     �%     �%     &  
   +&     6&     f   O       `                    V   J       6   )   %          7         $      i   _   U   j      L   K   n       ^   b                  B   ]   G   F   .   *   :               &   E          M   +   @   -   8      e   ;       1           Y   (               H       0          I           2   3   D         T   4   P      h      \   	   !   W   ,         X       d      o          k      9   S                   g   C   5      ?   N      /       
   [   R           Q   c   m           A   '             <   l      Z   >   =   #          a                  "    <div>
                    <p>
                        Hello,
                        <br/>
                        <br/>
                        The user ${object.applicant_uid.name} have tried to ${object.name}. But it needs your authorization to continue with the process.
                    </p>
                    <p>
                        Te reason is:
                        <br/>
                        ${object.reason}
                    </p>
                    Please take a look to the task:
                    <div style="text-align: center; margin: 16px 0px 16px 0px;">
                        <a href="${object.task_url}" style="background-color:#875A7B;padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">
                            View
                        </a>
                    </div>
                    <br/>
                    Thank you,
                    <br/>
                    % if object.applicant_uid and object.applicant_uid.signature:
                        ${object.applicant_uid.signature | safe}
                    % endif
                </div>
             <span>Authorize</span> <span>Reject</span> Action Needed Action date Action repsonsible Activities Activity Exception Decoration Activity State Additional viewers After condition Applicant Applicant user Ask for authorization Ask for changes Assigned Assigned to me Assigned user Attachment Count Authorization Date Authorization policies Authorization policy Authorization task Authorization tasks Authorization tasks dashboard Authorization: ${object.name} Authorizations Authorizations management Authorizator user Authorize Authorized Authorizer Before condition Configuration Created by Created on Default authorizer Default description Default priority Display Name Draft Followers Followers (Channels) Followers (Partners) Group By Hide Button Authorize Hide Task High Icon Icon to indicate an exception activity. If checked, new messages require your attention. If checked, some messages have a delivery error. Is Follower Last Modified on Last Updated by Last Updated on Low Main Main Attachment Medium Message Delivery error Messages Model My requests Name New values after authorize. Next Activity Deadline Next Activity Summary Next Activity Type Notified Emails Notified authorizers Number of Actions Number of errors Number of messages which requires an action Number of messages with delivery error Number of unread messages Object Partners with Need Action Pending Please specify a reason to authorize. Policies Policy Priority Reason Recipients Record Reject Rejected Request Date Responsible User Search tasks Show Form Some changes need to be authorized, but there is an existing authorization proceess for this record. Please check authorizations to send. Some changes require an authorization to continue. Please clic Actions/Ask for changes to specify a reason and continue. State Status based on activities
Overdue: Due date is already passed
Today: Activity date is today
Planned: Future activities. Task Url Tasks Tasks that I requested Tasks that are assigned to me Technical There is no authorization pending. Type of the exception activity on record. Unread Messages Unread Messages Counter Very High authorization.policy authorization.task policys tasks Project-Id-Version: Odoo Server 13.0-20220609
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2022-07-06 20:27-0500
Last-Translator: 
Language-Team: 
Language: es_MX
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: 
X-Generator: Poedit 3.1
 <div>
                    <p>
                        Hola,
                        <br/>
                        <br/>
                        El usuario ${object.applicant_uid.name} ha intentado ${object.name}. Pero necesita de su autorización para continuar con el proceso.
                    </p>
                    <p>
                        La razón es:
                        <br/>
                        ${object.reason}
                    </p>
                    Por favor revise esta solicitud:
                    <div style="text-align: center; margin: 16px 0px 16px 0px;">
                        <a href="${object.task_url}" style="background-color:#875A7B;padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">
                            Revisar
                        </a>
                    </div>
                    <br/>
                    Gracias,
                    <br/>
                    % if object.applicant_uid and object.applicant_uid.signature:
                        ${object.applicant_uid.signature | safe}
                    % endif
                </div>
             <span>Autorizar</span> <span>Rechazar</span> Acciones necesarias Fecha de acción Responsable Actividades Decoración de Actividad de Excepción Estado de la actividad Visores adicionales Condición (después) Solicitante Usuario solicitante Solicitar autorización Solicitar autorización Por autorizar Asignadas a mí Por autorizar Conteo de archivos adjuntos Fecha de acción Políticas de autorización Política de autorización Solicitud de autorización Solicitudes de autorización Dashboard de solicitudes de autorización Autorización: ${object.name} Autorizaciones Gestión de autorizaciones Usuario autorizado Autorizar Autorizada Autorizador Condición (antes) Configuración Creado por Creado en Autorizador por defecto Descripción por defecto Prioridad por defecto Nombre mostrado Borrador Seguidores Seguidores (Canales) Seguidores (Empresas) Agrupar por Ocultar botón de autorización Ocultar tarea Alta Icono Icono para indicar una actividad de excepción. Si está marcada, los nuevos mensajes requieren su atención. Si está marcada, algunos mensajes tienen un error de entrega. Es un seguidor Última modificación Modificado por Actualizado en Baja Inicio Adjuntos principales Media Error de Envío de Mensaje Mensajes Modelo Mis solicitudes Nombre Nuevos valores después de autorizar Siguiente plazo de actividad Resumen de la siguiente actividad Siguiente tipo de actividad Emails de notificados Autorizadores notificados Número de acciones Número de errores Número de mensajes que requieren una acción Número de mensajes con error de envío Número de mensajes no leidos Objeto Asociados con acción requerida Pendiente Especifique una razón para la autorización. Políticas Política Prioridad Razón Destinatarios Registro Rechazar Rechazada Fecha de solicitud Usuario responsable Buscar solicitudes Mostrar formulario Algunos cambios necesitan ser autorizados, pero ya existe un proceso de autorización para este registro. Por favor verifique las autorizaciones por enviar. Algunos cambios requieren de autorización para continuar. Haga clic en Acción / Solicitar autorización para especificar una razón del cambio y continuar. Estatus Estado basado en actividades
Vencida: la fecha tope ya ha pasado
Hoy: La fecha tope es hoy
Planificada: futuras actividades. URL de la solicitud Solicitudes Solicitadas por mí Asignadas a mí Técnico No hay autorizaciones por enviar Tipo de actividad de excepción registrada. Mensajes sin leer Contador de mensajes sin leer Muy alta Política de autorización Solicitud de autorización Políticas Solicitudes 