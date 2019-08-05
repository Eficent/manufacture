# Copyright 2019 Eficent
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResUsers(models.Model):

    _inherit = 'res.users'

    repair_team_id = fields.Many2one(
        'repair.team', "Default Repair Team"
    )

    repair_team_ids = fields.Many2many(
        string='Repair Teams',
        comodel_name='repair.team',
        relation='mrp_repair_team_user_rel',
        column1='user_id', column2='team_id')
