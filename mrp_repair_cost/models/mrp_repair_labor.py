# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError

UNIT = dp.get_precision('Product Price')


class MrpRepairLabor(models.Model):
    _name = 'mrp.repair.labor'

    name = fields.Char()
    cost = fields.Float(digits=UNIT)
    repair_id = fields.Many2one('mrp.repair')
    journal_id = fields.Many2one('account.journal')
    credit_account_id = fields.Many2one('account.account')
    debit_account_id = fields.Many2one('account.account')

    @api.multi
    def _prepare_account_move_line(self):
        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        res = []
        for labor in self:
            debit_value = self.repair_id.company_id.currency_id.round(labor.cost)

            # check that all data is correct
            if self.repair_id.company_id.currency_id.is_zero(debit_value) and not self.env['ir.config_parameter'].sudo().get_param('stock_account.allow_zero_cost'):
                raise ValidationError(_("The cost of %s is currently equal to 0. Change the cost or the labor") % (self.product_id.display_name,))
            partner_id = (self.repair_id.partner_id and self.env['res.partner']._find_accounting_partner(self.repair_id.partner_id).id) or False
            debit_line_vals = {
                'name': self.repair_id.name,  #  as in standard when moving to production location
                'ref': self.name,
                'partner_id': partner_id,
                'debit': debit_value if debit_value > 0 else 0,
                'credit': -debit_value if debit_value < 0 else 0,
                'account_id': labor.repair_id.type_id.debit_account_id.id,
            }
            res += [(0, 0, debit_line_vals)]
        credit_value = sum(self.mapped('cost'))
        credit_line_vals = {
            'name': self.repair_id.name,
            'ref': self.name,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': self.repair_id.type_id.credit_labor_account_id.id,
        }
        res += [(0, 0, credit_line_vals)]
        return res
