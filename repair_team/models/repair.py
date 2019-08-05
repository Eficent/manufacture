# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpRepair(models.Model):
    _inherit = 'repair.order'

    @api.model
    def default_team_id(self):
        return self.env.user.repair_team_id or False

    type_id = fields.Many2one('repair.type',
                              company_dependent=True)
    team_id = fields.Many2one(
        'repair.team', default=default_team_id)

    @api.onchange('type_id')
    def onchange_type_id(self):
        if not self.type_id:
            return
        self.under_warranty = self.type_id.under_warranty
        self.to_refurbish = self.type_id.to_refurbish
        for line in self.operations:
            line.location_dest_id = self.type_id.\
                default_raw_material_prod_location_id

    @api.onchange('team_id')
    def onchange_team_id(self):
        if not self.team_id:
            return
        self.location_id = \
            self.team_id.default_repair_src_location_id
        self.location_dest_id = \
            self.team_id.default_repair_dest_location_id
        for line in self.operations:
            line.location_id = self.team_id.\
                default_raw_material_location_id
