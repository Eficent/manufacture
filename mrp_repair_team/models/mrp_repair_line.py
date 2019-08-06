# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpRepair(models.Model):
    _inherit = 'mrp.repair.line'

    @api.model
    def default_location_id(self):
        if self.env.context.get('team_id', False):
            team = self.env['mrp.repair.team'].browse(
                self.env.context.get('team_id'))
            return team.default_raw_material_location_id.id

    @api.model
    def default_location_dest_id(self):
        if self.env.context.get('type_id', False):
            rtype = self.env['mrp.repair.type'].browse(
                self.env.context.get('type_id'))
            return rtype.default_raw_material_prod_location_id.id

    location_id = fields.Many2one(default=default_location_id)
    location_dest_id = fields.Many2one(default=default_location_dest_id)

    @api.onchange('type', 'repair_id')
    def onchange_operation_type(self):
        res = super(MrpRepair, self).onchange_operation_type()
        self.repair_id.onchange_type_id()

        if not self.type or self.type == 'add':
            self.location_id = self.default_location_id()
            self.location_dest_id = self.default_location_dest_id()
        return res
