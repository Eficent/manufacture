# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        super()._onchange_bom_id()
        self.user_id = self.bom_id.user_id

    @api.model
    def create(self, vals):
        bom_id = vals.get('bom_id', False)
        if bom_id:
            vals['user_id'] = self.env['mrp.bom'].browse(bom_id).user_id.id
        return super().create(vals)
