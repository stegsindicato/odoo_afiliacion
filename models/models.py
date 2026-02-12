# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from odoo import api, fields, models
from urllib.parse import quote_plus

class ResPartner(models.Model):
    _inherit = "res.partner"

    # --- Marcadores de tipo ---
    e_afiliado = fields.Boolean(string="É afiliado", index=True)
    e_centro_educativo = fields.Boolean(string="É centro educativo", index=True)

    # =========================
    # Afiliación (Afiliado)
    # =========================
    dni = fields.Char(string="DNI/NIF", index=True)
    numero_afiliado = fields.Char(string="Nº afiliado", index=True)

    data_alta = fields.Date(string="Data de alta")
    data_baixa = fields.Date(string="Data de baixa")

    xenero = fields.Selection(
        [
            ("home", "Home"),
            ("muller", "Muller"),
            ("outro", "Outro"),
            ("nsnc", "Prefiro non dicilo"),
        ],
        string="Xénero",
    )

    data_nacemento = fields.Date(string="Data de nacemento")

    sede = fields.Selection(
        [
            ("coruna", "A Coruña"),
            ("lugo", "Lugo"),
            ("ourense", "Ourense"),
            ("pontevedra", "Pontevedra"),
        ],
        string="Sede",
        index=True,
    )

    especialidade_id = fields.Many2one(
        "sindicato.especialidade",
        string="Especialidade",
    )

    centro_traballo_id = fields.Many2one(
        "res.partner",
        string="Centro de traballo",
        domain="[('e_centro_educativo', '=', True)]",
    )

    situacion_laboral = fields.Selection(
        [
            ("paro", "Paro"),
            ("provisional", "Provisional"),
            ("interino", "Interino"),
            ("definitivo", "Definitivo"),
        ],
        string="Situación laboral",
        index=True,
    )

    tipo_cota_id = fields.Many2one(
        "sindicato.tipo.cota",
        string="Tipo de cota",
    )

    afiliacion_activa = fields.Boolean(
        string="Afiliación activa",
        compute="_compute_afiliacion_activa",
        store=True,
        index=True,
    )

    @api.depends("data_alta", "data_baixa", "e_afiliado")
    def _compute_afiliacion_activa(self):
        hoxe = fields.Date.today()
        for rex in self:
            if not rex.e_afiliado or not rex.data_alta:
                rex.afiliacion_activa = False
                continue
            rex.afiliacion_activa = bool(
                rex.data_alta <= hoxe and (not rex.data_baixa or rex.data_baixa >= hoxe)
            )

    # =========================
    # Centro educativo
    # =========================
    codigo_centro = fields.Char(string="Código de centro", index=True)

    afiliados_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="centro_traballo_id",
        string="Afiliados do centro",
        domain=[("e_afiliado", "=", True)],
    )

    ligazon_google_maps = fields.Char(
        string="Google Maps",
        compute="_compute_ligazons_gps",
        store=False,
    )
    ligazon_osm = fields.Char(
        string="OpenStreetMap",
        compute="_compute_ligazons_gps",
        store=False,
    )

    @api.depends("partner_latitude", "partner_longitude")
    def _compute_ligazons_gps(self):
        for rex in self:
            lat = rex.partner_latitude
            lon = rex.partner_longitude
            if not lat or not lon:
                rex.ligazon_google_maps = False
                rex.ligazon_osm = False
                continue

            q = quote_plus(f"{lat},{lon}")
            rex.ligazon_google_maps = f"https://www.google.com/maps?q={q}"
            rex.ligazon_osm = (
                f"https://www.openstreetmap.org/"
                f"?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}"
            )


# =========================
# Especialidades (con corpo)
# =========================
class SindicatoEspecialidade(models.Model):
    _name = "sindicato.especialidade"
    _description = "Especialidade docente"
    _order = "corpo, nome"
    _rec_name = "nome"

    nome = fields.Char(string="Nome da especialidade", required=True, translate=True)

    corpo = fields.Selection(
        [
            ("590", "590 · Corpo de Profesores de Ensino Secundario"),
            ("591", "591 · Corpo de Profesores Técnicos de Formación Profesional"),
            ("592", "592 · Corpo de Profesores de Escolas Oficiais de Idiomas"),
            ("594", "594 · Corpo de Profesores de Música e Artes Escénicas"),
            ("595", "595 · Corpo de Profesores de Artes Plásticas e Deseño"),
            ("596", "596 · Corpo de Mestres de Taller de Artes Plásticas e Deseño"),
            ("597", "597 · Corpo de Mestres"),
        ],
        string="Corpo",
        required=True,
        index=True,
    )

    codigo_oficial = fields.Char(
        string="Código oficial",
        help="Código da especialidade segundo a normativa (ex. 006, 107, etc.)",
        index=True,
    )

    activo = fields.Boolean(string="Activo", default=True)


# =========================
# Tipos de cota
# =========================
class SindicatoTipoCota(models.Model):
    _name = "sindicato.tipo.cota"
    _description = "Tipo de cota"
    _rec_name = "nome"

    nome = fields.Char(string="Nome", required=True, translate=True)
    activo = fields.Boolean(string="Activo", default=True)
