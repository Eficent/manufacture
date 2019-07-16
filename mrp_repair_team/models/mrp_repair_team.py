# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpRepairTeam(models.Model):
    _name = 'mrp.repair.team'

    name = fields.Char()
    default_raw_material_location_id = fields.Many2one(
        'stock.location',
        string="Raw material source location",
        required=True)
    user_ids = fields.Many2many(
        'res.users',
        string='Users')
