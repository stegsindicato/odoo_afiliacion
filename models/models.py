# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from odoo import api, fields, models
from urllib.parse import quote_plus
from odoo.osv import expression

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

    anos_afiliacion = fields.Integer(
        string="Antiguedade afiliación (anos)",
        compute="_compute_anos_afiliacion",
        store=True,
    )

    @api.depends("data_alta", "data_baixa", "e_afiliado")
    def _compute_anos_afiliacion(self):
        hoxe = fields.Date.today()
        for rex in self:
            rex.anos_afiliacion = 0

            if not rex.e_afiliado or not rex.data_alta:
                continue

            data_fin = rex.data_baixa or hoxe
            if data_fin < rex.data_alta:
                continue

            anos = data_fin.year - rex.data_alta.year
            if (data_fin.month, data_fin.day) < (rex.data_alta.month, rex.data_alta.day):
                anos -= 1

            rex.anos_afiliacion = max(anos, 0)

    xenero = fields.Selection(
        [
            ("home", "Home"),
            ("muller", "Muller"),
            ("outro", "Outro"),
            ("nsnc", "Prefiro non dicilo"),
        ],
        string="Xénero",
    )

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

    historial_profesional_ids = fields.One2many(
        "sindicato.afiliado.historial",
        "partner_id",
        string="Historial profesional",
    )

    centro_traballo_id = fields.Many2one(
        "res.partner",
        string="Centro de traballo",
        compute="_compute_situacion_profesional_actual",
        store=True,
    )

    especialidade_id = fields.Many2one(
        "sindicato.especialidade",
        string="Especialidade",
        compute="_compute_situacion_profesional_actual",
        store=True,
    )

    situacion_laboral = fields.Selection(
        [
            ("paro", "Paro"),
            ("provisional", "Provisional"),
            ("interino", "Interino/a"),
            ("substituto", "Substituto/a"),
            ("definitivo", "Definitivo/a"),
            ("xubilado", "Xubilado/a")
        ],
        string="Situación laboral",
        compute="_compute_situacion_profesional_actual",
        store=True,
        index=True,
    )

    @api.depends(
        "historial_profesional_ids.data_cambio",
        "historial_profesional_ids.centro_id",
        "historial_profesional_ids.especialidade_id",
        "historial_profesional_ids.situacion_laboral",
    )
    def _compute_situacion_profesional_actual(self):
        hoxe = fields.Date.today()
        data_min = fields.Date.to_date("1900-01-01")

        for rex in self:
            rex.centro_traballo_id = False
            rex.especialidade_id = False
            rex.situacion_laboral = False

            historial_vixente = rex.historial_profesional_ids.filtered(
                lambda r: r.data_cambio and r.data_cambio <= hoxe
            ).sorted(
                key=lambda r: (r.data_cambio or data_min, r.id),
                reverse=True,
            )

            if historial_vixente:
                ultimo = historial_vixente[0]
                rex.centro_traballo_id = ultimo.centro_id
                rex.especialidade_id = ultimo.especialidade_id
                rex.situacion_laboral = ultimo.situacion_laboral

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

    @api.model
    def cron_recompute_situacion_profesional(self):
        afiliados = self.search([("e_afiliado", "=", True)])
        afiliados._compute_situacion_profesional_actual()

    # =========================
    # Centro educativo
    # =========================
    codigo_centro = fields.Char(string="Código de centro", index=True)

    afiliados_actuales_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Afiliados actuais",
        compute="_compute_afiliados_actuales_ids",
    )

    def _compute_afiliados_actuales_ids(self):
        Partner = self.env["res.partner"].with_context(active_test=False)

        for centro in self:
            if not centro.e_centro_educativo:
                centro.afiliados_actuales_ids = False
                continue

            centro.afiliados_actuales_ids = Partner.search([
                ("e_afiliado", "=", True),
                ("centro_traballo_id", "=", centro.id),
            ])

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
            ("598", "598 · Corpo de Profesores Especialistas en Sectores Singulares de Formación Profesional"),
            ("510", "510 · Corpo de Inspectores"),
            ("---", "--- · Outros")
        ],
        string="Corpo",
        required=True,
        index=True,
    )

    activo = fields.Boolean(string="Activo", default=True)

    codigo_oficial = fields.Char(
        string="Código oficial",
        help="Código da especialidade segundo a normativa (ex. 006, 107, etc.)",
        index=True,
    )

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        domain = []

        if name:
            domain = expression.OR([
                [("nome", operator, name)],
                [("codigo_oficial", operator, name)],
                [("corpo", operator, name)],
            ])

        records = self.search(expression.AND([args, domain]), limit=limit)
        return [(r.id, r.display_name) for r in records]

# =========================
# Tipos de cota
# =========================
class SindicatoTipoCota(models.Model):
    _name = "sindicato.tipo.cota"
    _description = "Tipo de cota"
    _rec_name = "nome"

    nome = fields.Char(string="Nome", required=True, translate=True)
    cantidade = fields.Float(string="Cantidade", required=True)
    activo = fields.Boolean(string="Activo", default=True)


# =========================
# Historial profesional do afiliado
# =========================
class SindicatoAfiliadoHistorial(models.Model):
    _name = "sindicato.afiliado.historial"
    _description = "Historial profesional do afiliado"
    _order = "data_cambio desc, id desc"

    partner_id = fields.Many2one(
        "res.partner",
        string="Afiliado",
        required=True,
        ondelete="cascade",
        index=True,
    )

    data_cambio = fields.Date(
        string="Data do cambio",
        required=True,
        index=True,
    )

    centro_id = fields.Many2one(
        "res.partner",
        string="Centro",
        domain="[('e_centro_educativo', '=', True)]",
    )

    especialidade_id = fields.Many2one(
        "sindicato.especialidade",
        string="Especialidade",
    )

    situacion_laboral = fields.Selection(
        [
            ("paro", "Paro"),
            ("provisional", "Provisional"),
            ("interino", "Interino/a"),
            ("substituto", "Substituto/a"),
            ("definitivo", "Definitivo/a"),
            ("xubilado", "Xubilado/a")
        ],
        string="Situación laboral",
        index=True,
    )

    observacions = fields.Text(string="Observacións")

    @api.constrains("partner_id")
    def _check_partner_is_afiliado(self):
        for rex in self:
            if rex.partner_id and not rex.partner_id.e_afiliado:
                raise ValidationError(
                    "O historial profesional só se pode asignar a afiliados."
                )

    @api.constrains("centro_id")
    def _check_centro_is_centro_educativo(self):
        for rex in self:
            if rex.centro_id and not rex.centro_id.e_centro_educativo:
                raise ValidationError(
                    "O centro indicado debe ser un centro educativo."
                )