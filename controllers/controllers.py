# -*- coding: utf-8 -*-
# from odoo import http


# class StegAfiliacion(http.Controller):
#     @http.route('/steg_afiliacion/steg_afiliacion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/steg_afiliacion/steg_afiliacion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('steg_afiliacion.listing', {
#             'root': '/steg_afiliacion/steg_afiliacion',
#             'objects': http.request.env['steg_afiliacion.steg_afiliacion'].search([]),
#         })

#     @http.route('/steg_afiliacion/steg_afiliacion/objects/<model("steg_afiliacion.steg_afiliacion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('steg_afiliacion.object', {
#             'object': obj
#         })

