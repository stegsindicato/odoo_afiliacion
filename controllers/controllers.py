# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.http import request
from markupsafe import Markup

_logger = logging.getLogger(__name__)


class StegAfiliacionController(http.Controller):

    def _get_next_numero_afiliado(self, Partner):
        partners = Partner.search(
            [
                ('e_afiliado', '=', True),
                ('numero_afiliado', '!=', False),
            ],
            order='numero_afiliado desc',
            limit=50,
        )

        max_number = 0
        for partner in partners:
            value = (partner.numero_afiliado or '').strip()
            if value.isdigit():
                max_number = max(max_number, int(value))

        return str(max_number + 1)

    def _build_form_texts(self, values):
        firstname = values.get('firstname', '')
        lastname = values.get('lastname', '')
        full_name = values.get('full_name', '')
        dni = values.get('dni', '')
        birthdate = values.get('birthdate', '')
        street = values.get('street', '')
        city = values.get('city', '')
        municipio = values.get('municipio', '')
        provincia = values.get('provincia', '')
        zip_code = values.get('zip_code', '')
        phone = values.get('phone', '')
        mobile = values.get('mobile', '')
        email = values.get('email', '')
        sede = values.get('sede', '')
        corpo = values.get('corpo', '')
        especialidade = values.get('especialidade', '')
        situacion_laboral = values.get('situacion_laboral', '')
        centro_destino = values.get('centro_destino', '')
        iban = values.get('iban', '')
        rgpd_aceptado = values.get('rgpd_aceptado', False)
        rgpd_fecha = values.get('rgpd_fecha', '')
        rgpd_ip = values.get('rgpd_ip', '')
        user_agent = values.get('user_agent', '')

        form_text_plain = (
            "=== DATOS FORMULARIO WEB ===\n\n"
            f"Nome: {firstname or '-'}\n"
            f"Apelidos: {lastname or '-'}\n"
            f"Nome completo: {full_name or '-'}\n"
            f"DNI: {dni or '-'}\n\n"
            f"Data de nacemento: {birthdate or '-'}\n\n"
            f"Enderezo: {street or '-'}\n"
            f"Localidade: {city or '-'}\n"
            f"Concello/Municipio: {municipio or '-'}\n"
            f"Provincia: {provincia or '-'}\n"
            f"CP: {zip_code or '-'}\n\n"
            f"Teléfono fixo: {phone or '-'}\n"
            f"Teléfono móbil: {mobile or '-'}\n"
            f"Email: {email or '-'}\n\n"
            f"Sede: {sede or '-'}\n"
            f"Corpo: {corpo or '-'}\n"
            f"Especialidade: {especialidade or '-'}\n"
            f"Situación laboral: {situacion_laboral or '-'}\n"
            f"Centro de destino: {centro_destino or '-'}\n\n"
            f"IBAN: {iban or '-'}\n\n"
            f"RGPD aceptado: {'si' if rgpd_aceptado else 'non'}\n"
            f"Data aceptación RGPD: {rgpd_fecha or '-'}\n"
            f"IP orixe: {rgpd_ip or '-'}\n"
            f"User-Agent: {user_agent or '-'}\n\n"
            f"Orixe: formulario online STEG"
        )

        form_text_html = (
            "Datos recibidos desde formulario web:<br/>"
            "<ul>"
            f"<li><b>Nome:</b> {firstname or '-'}</li>"
            f"<li><b>Apelidos:</b> {lastname or '-'}</li>"
            f"<li><b>Nome completo:</b> {full_name or '-'}</li>"
            f"<li><b>DNI:</b> {dni or '-'}</li>"
            f"<li><b>Data de nacemento:</b> {birthdate or '-'}</li>"
            f"<li><b>Enderezo:</b> {street or '-'}</li>"
            f"<li><b>Localidade:</b> {city or '-'}</li>"
            f"<li><b>Concello/Municipio:</b> {municipio or '-'}</li>"
            f"<li><b>Provincia:</b> {provincia or '-'}</li>"
            f"<li><b>CP:</b> {zip_code or '-'}</li>"
            f"<li><b>Teléfono fixo:</b> {phone or '-'}</li>"
            f"<li><b>Teléfono móbil:</b> {mobile or '-'}</li>"
            f"<li><b>Email:</b> {email or '-'}</li>"
            f"<li><b>Sede:</b> {sede or '-'}</li>"
            f"<li><b>Corpo:</b> {corpo or '-'}</li>"
            f"<li><b>Especialidade:</b> {especialidade or '-'}</li>"
            f"<li><b>Situación laboral:</b> {situacion_laboral or '-'}</li>"
            f"<li><b>Centro de destino:</b> {centro_destino or '-'}</li>"
            f"<li><b>IBAN:</b> {iban or '-'}</li>"
            f"<li><b>RGPD aceptado:</b> {'si' if rgpd_aceptado else 'non'}</li>"
            f"<li><b>Data aceptación RGPD:</b> {rgpd_fecha or '-'}</li>"
            f"<li><b>IP orixe:</b> {rgpd_ip or '-'}</li>"
            f"<li><b>User-Agent:</b> {user_agent or '-'}</li>"
            f"<li><b>Orixe:</b> formulario online STEG</li>"
            "</ul>"
        )

        return form_text_plain, form_text_html

    @http.route(
        '/api/solicitude-afiliacion',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False
    )
    def solicitude_afiliacion(self, **kwargs):
        token = request.httprequest.headers.get('X-STEG-Token')
        expected_token = request.env['ir.config_parameter'].sudo().get_param(
            'steg_afiliacion.api_token'
        )

        if not expected_token or token != expected_token:
            _logger.warning("Solicitud rechazada por token inválido")
            return {
                'ok': False,
                'error': 'unauthorized',
                'message': 'Token non válido',
            }

        data = request.get_json_data() or {}
        params = data.get('params', data)

        odoo_bot = request.env.ref('base.partner_root')

        _logger.info("Nova solicitude web recibida: %s", params)

        firstname = (params.get('firstname') or '').strip()
        lastname = (params.get('lastname') or '').strip()
        dni = (params.get('dni') or '').strip().upper()
        birthdate = (params.get('birthdate') or '').strip()

        street = (params.get('street') or '').strip()
        city = (params.get('city') or '').strip()
        municipio = (params.get('municipio') or '').strip()
        provincia = (params.get('provincia') or '').strip()
        zip_code = (params.get('zip') or '').strip()

        phone = (params.get('phone') or '').strip()
        mobile = (params.get('mobile') or '').strip()
        email = (params.get('email') or '').strip().lower()

        sede = (params.get('sede') or '').strip()
        corpo = (params.get('corpo') or '').strip()
        especialidade = (params.get('especialidade') or '').strip()
        situacion_laboral = (params.get('situacion_laboral') or '').strip()
        centro_destino = (params.get('centro_destino') or '').strip()

        iban = (params.get('iban') or '').replace(' ', '').upper()

        rgpd_aceptado = params.get('rgpd_aceptado')
        rgpd_fecha = (params.get('rgpd_fecha') or '').strip()

        rgpd_ip = (
            request.httprequest.headers.get('X-Forwarded-For')
            or request.httprequest.remote_addr
            or ''
        ).strip()
        user_agent = (request.httprequest.headers.get('User-Agent') or '').strip()

        if not firstname or not lastname or not dni or not email:
            return {
                'ok': False,
                'error': 'missing_required_fields',
                'message': 'Faltan campos obrigatorios: firstname, lastname, dni, email',
            }

        Partner = request.env['res.partner'].sudo()
        PartnerBank = request.env['res.partner.bank'].sudo()

        form_values = {
            'firstname': firstname,
            'lastname': lastname,
            'dni': dni,
            'birthdate': birthdate,
            'street': street,
            'city': city,
            'municipio': municipio,
            'provincia': provincia,
            'zip_code': zip_code,
            'phone': phone,
            'mobile': mobile,
            'email': email,
            'sede': sede,
            'corpo': corpo,
            'especialidade': especialidade,
            'situacion_laboral': situacion_laboral,
            'centro_destino': centro_destino,
            'iban': iban,
            'rgpd_aceptado': rgpd_aceptado,
            'rgpd_fecha': rgpd_fecha,
            'rgpd_ip': rgpd_ip,
            'user_agent': user_agent,
        }

        form_text_plain, form_text_html = self._build_form_texts(form_values)

        existing = Partner.search([
            '|',
            ('dni', '=', dni),
            ('email', '=', email),
        ], limit=1)

        if existing:
            existing.message_post(
                body=Markup((
                    "Nova solicitude web detectada, pero non se creou un novo afiliado "
                    "por posible duplicado.<br/><br/>"
                    f"{form_text_html}"
                )),
                message_type='comment',
                subtype_xmlid='mail.mt_note',
                author_id=odoo_bot.id,
            )

            _logger.info(
                "Solicitude duplicada detectada para partner %s (dni=%s, email=%s)",
                existing.id, dni, email
            )

            return {
                'ok': False,
                'error': 'already_exists',
                'message': 'Xa existe un contacto con ese DNI ou email',
                'partner_id': existing.id,
            }

        numero_afiliado = self._get_next_numero_afiliado(Partner)

        vals = {
            'firstname': firstname,
            'lastname': lastname,
            'dni': dni,
            'numero_afiliado': numero_afiliado,
            'email': email,
            'phone': phone,
            'mobile': mobile,
            'street': street,
            'city': city,
            'zip': zip_code,
            'e_afiliado': True,
        }

        partner = Partner.create(vals)

        if iban:
            existing_bank = PartnerBank.search([
                ('acc_number', '=', iban),
            ], limit=1)

            if not existing_bank:
                PartnerBank.create({
                    'partner_id': partner.id,
                    'acc_number': iban,
                })
            else:
                partner.message_post(
                    body=Markup((
                        "Non se creou a conta bancaria porque xa existe unha conta "
                        f"co IBAN {iban} na base de datos."
                    )),
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                    author_id=odoo_bot.id,
                )

        partner.message_post(
            body=Markup((
                "Afiliado creado automaticamente desde o formulario web.<br/><br/>"
                f"<p><b>Número de afiliado asignado:</b> {numero_afiliado}</p>"
                f"{form_text_html}"
            )),
            message_type='comment',
            subtype_xmlid='mail.mt_note',
            author_id=odoo_bot.id,
        )

        _logger.info(
            "Afiliado creado desde web: partner_id=%s, numero_afiliado=%s",
            partner.id, numero_afiliado
        )

        return {
            'ok': True,
            'partner_id': partner.id,
            'name': partner.name,
            'numero_afiliado': numero_afiliado,
        }