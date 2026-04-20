# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID, fields


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    Partner = env["res.partner"]
    Historial = env["sindicato.afiliado.historial"]

    afiliados = Partner.search([
        ("e_afiliado", "=", True),
        "|", "|",
        ("centro_traballo_id", "!=", False),
        ("especialidade_id", "!=", False),
        ("situacion_laboral", "!=", False),
    ])

    hoxe = fields.Date.today()

    for afiliado in afiliados:
        # Evitar duplicados: si ya tiene historial, no hacemos nada
        if afiliado.historial_profesional_ids:
            continue

        data_cambio = afiliado.data_alta
        if not data_cambio and afiliado.create_date:
            data_cambio = fields.Date.to_date(afiliado.create_date)
        if not data_cambio:
            data_cambio = hoxe

        Historial.create({
            "partner_id": afiliado.id,
            "data_cambio": data_cambio,
            "centro_id": afiliado.centro_traballo_id.id or False,
            "especialidade_id": afiliado.especialidade_id.id or False,
            "situacion_laboral": afiliado.situacion_laboral or False,
            "observacions": "Migrado automaticamente desde os campos profesionais anteriores.",
        })