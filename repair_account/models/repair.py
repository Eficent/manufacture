# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    timesheet_ids = fields.One2many('account.analytic.line', 'repair_id',
                                    string="Analytic Lines")

    @api.onchange('type_id')
    def onchange_type_id(self):
        super(RepairOrder, self).onchange_type_id()
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
        if self.to_refurbish and self.type_id.refurbish_location_id:
            self.location_dest_id = self.type_id.refurbish_location_id

    def allocate_cost(self):
        for rec in self:
            move_lines = rec._prepare_account_move_line('labor')
            move_lines += rec._prepare_account_move_line('overhead')
            if move_lines:
                date = self._context.get('force_period_date',
                                         fields.Date.context_today(self))
                new_account_move = self.env['account.move'].sudo().create({
                    'journal_id': self.team_id.journal_id.id,
                    'line_ids': move_lines,
                    'date': date,
                    'ref': self.name
                })
                new_account_move.post()

    @api.multi
    def action_repair_end(self):
        res = super(RepairOrder, self).action_repair_end()
        self.allocate_cost()
        return res

    @api.multi
    def _prepare_account_move_line(self, cost_type):
        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        res = []
        self.ensure_one()
        valuation_amount = self.get_cost_amount(cost_type)

        credit_account_id, debit_account_id, journal_id = \
            self.get_accounting_data_for_non_material(cost_type)

        # the standard_price of the product may be in another decimal
        # precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating
        # the accounting entries.
        debit_value = self.company_id.currency_id.round(
            valuation_amount)
        # check that all data is correct
        if self.company_id.currency_id.is_zero(debit_value) and not self.env['ir.config_parameter'].sudo().get_param('stock_account.allow_zero_cost'):
            raise ValidationError(_("The cost of %s is currently equal to 0. Change the cost in the repair team") % (cost_type,))
        partner_id = (self.partner_id and self.env['res.partner']._find_accounting_partner(self.partner_id).id) or False
        debit_line_vals = {
            'name': self.name,  #  as in standard when moving to production location
            'ref': self.name,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id.id,
        }
        res += [(0, 0, debit_line_vals)]
        credit_value = debit_value
        credit_line_vals = {
            'name': self.name,
            'ref': self.name,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id.id
        }
        res += [(0, 0, credit_line_vals)]
        return res

    def get_accounting_data_for_non_material(self, cost_type):
        """ Return the accounts and journal to use to post Journal Entries """
        if cost_type == 'labor':
            all_account = self.team_id.labor_allocation_account_id
        elif cost_type == 'overhead':
            all_account = self.team_id.overhead_allocation_account_id
        else:
            raise ValidationError('Undefined cost type')
        wip_account = self.type_id.wip_account_id
        stock_journal = self.team_id.journal_id
        return all_account, wip_account, stock_journal

    def get_cost_amount(self, cost_type):
        if cost_type == 'labor':
            return self.team_id.labor_standard_cost
        elif cost_type == 'overhead':
            return self.team_id.overhead_standard_cost
        else:
            raise ValidationError('Undefined cost type')

    def action_view_account_moves(self):
        self.ensure_one()
        action = self.env.ref('account.action_account_moves_all_a')
        result = action.read()[0]
        result['domain'] = [('name', '=', self.name)]
        return result
