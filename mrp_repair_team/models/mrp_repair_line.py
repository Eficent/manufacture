# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpRepair(models.Model):
    _inherit = 'mrp.repair.line'

    @api.model
    def default_location_id(self):
        if self.repair_id.team_id:
            return self.repair_id.team_id.\
                default_raw_material_location_id.id

    @api.model
    def default_location_dest_id(self):
        if self.repair_id.type_id:
            return self.repair_id.type_id.\
                default_raw_material_prod_location_id.id

    location_id = fields.Many2one(default=default_location_id)
    location_dest_id = fields.Many2one(default=default_location_dest_id)

    @api.onchange('type', 'repair_id')
    def onchange_operation_type(self):
        res = super(MrpRepair, self).onchange_operation_type()
        self.repair_id.onchange_type_id()
        return res
