# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    labor_line_ids = fields.One2many('mrp.repair.labor', 'repair_id')
    overhead_line_ids = fields.One2many('mrp.repair.overhead', 'repair_id')

    @api.onchange('type_id')
    def onchange_type_id(self):
        super(MrpRepair, self).onchange_type_id()
        if self.to_refurbish:
            self.location_dest_id = \
                self.type_id.default_raw_material_prod_location_id

    @api.onchange('to_refurbish', 'product_id')
    def _onchange_to_refurbish(self):
        if self.to_refurbish:
            self.refurbish_product_id = self.product_id.refurbish_product_id
            self.refurbish_location_dest_id = self.location_dest_id
        else:
            self.location_dest_id = self.refurbish_location_dest_id
            self.refurbish_product_id = False
            self.refurbish_location_dest_id = False

    def allocate_overhead_cost(self):
        for rec in self:
            if not rec.overhead_line_ids:
                return
            move_lines = rec.overhead_line_ids._prepare_account_move_line()
            if move_lines:
                date = self._context.get('force_period_date',
                                         fields.Date.context_today(self))
                new_account_move = self.env['account.move'].sudo().create({
                    'journal_id': self.type_id.journal_id.id,
                    'line_ids': move_lines,
                    'date': date,
                    'ref': self.name
                })
                new_account_move.post()

    def allocate_labor_cost(self):
        for rec in self:
            if not rec.labor_line_ids:
                return
            move_lines = rec.labor_line_ids._prepare_account_move_line()
            if move_lines:
                date = self._context.get('force_period_date',
                                         fields.Date.context_today(self))
                new_account_move = self.env['account.move'].sudo().create({
                    'journal_id': self.type_id.journal_id.id,
                    'line_ids': move_lines,
                    'date': date,
                    'ref': self.name
                })
                new_account_move.post()

    @api.multi
    def action_repair_end(self):
        res = super(MrpRepair, self).action_repair_end()
        self.allocate_labor_cost()
        self.allocate_overhead_cost()
        return res
