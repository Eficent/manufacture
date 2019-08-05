# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpRepairTeam(models.Model):
    _name = 'repair.team'

    name = fields.Char()
    default_raw_material_location_id = fields.Many2one(
        'stock.location',
        string="Raw material source location",
        required=True)
    user_ids = fields.Many2many(
        string='Users',
        comodel_name='res.users',
        relation='mrp_repair_team_user_rel',
        column1='team_id', column2='user_id')

    default_repair_src_location_id = fields.Many2one(
        'stock.location',
        string="Default location of the damaged product",
        required=False)
    default_repair_dest_location_id = fields.Many2one(
        'stock.location',
        string="Default destination location of the repaired product",
        required=False)
