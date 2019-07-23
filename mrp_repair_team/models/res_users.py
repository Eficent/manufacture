# Copyright 2019 Eficent
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResUsers(models.Model):

    _inherit = 'res.users'

    mrp_repair_team_id = fields.Many2one(
        'mrp.repair.team', "Default Repair Team"
    )
