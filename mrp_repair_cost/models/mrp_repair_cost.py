# Copyright 2018 Aleph Objects, Inc. (https://www.alephobjects.com)
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError

UNIT = dp.get_precision('Product Price')


class MrpRepairCost(models.Model):
    _name = "mrp.repair.cost"

    @api.model
    def default_product(self):
        if self.cost_type == 'labor':
            return self.type_id.default_labor_product_id
        else:
            return self.type_id.default_oh_product_id

    @api.model
    def default_cost_type(self):
        if self.env.context.get('default_cost_type', False):
            if self.env.context.get('default_cost_type') == 'labor':
                return 'labor'
            else:
                return 'overhead'

    name = fields.Char(related='product_id.name')
    cost_type = fields.Selection(
        string="Type",
        selection=[('labor', 'Labor'), ('overhead', 'Overhead')],
        deafult='default_cost_type',
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        domain=[('type', '=', 'service')],
    )
    product_qty = fields.Float(
        string='Product Quantity', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    product_uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='Product Unit of Measure',
        required=True,
    )
    repair_id = fields.Many2one('mrp.repair')

    @api.onchange('product_uom_id')
    def onchange_product_uom_id(self):
        res = {}
        if not self.product_uom_id or not self.product_id:
            return res
        if self.product_uom_id.category_id != \
                self.product_id.uom_id.category_id:
            self.product_uom_id = self.product_id.uom_id.id
            res['warning'] = {
                'title': _('Warning'),
                'message': _('The Product Unit of Measure you chose has a '
                             'different category than in the product form.'),
            }
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    @api.multi
    def _prepare_account_move_line(self):
        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        res = []
        credit_value = 0.0

        for cost_line in self:

            self.ensure_one()
            valuation_amount = abs(
                cost_line.product_id.standard_price) * cost_line.product_qty

            cost_type = cost_line.cost_type
            credit_account_id, debit_account_id, journal_id = \
                cost_line.product_id.product_tmpl_id.\
                get_accounting_data_for_non_material(cost_type)

            # the standard_price of the product may be in another decimal
            # precision, or not compatible with the coinage of
            # the company currency... so we need to use round() before creating
            # the accounting entries.
            debit_value = self.repair_id.company_id.currency_id.round(
                valuation_amount)
            credit_value += debit_value
            # check that all data is correct
            if self.repair_id.company_id.currency_id.is_zero(debit_value) and not self.env['ir.config_parameter'].sudo().get_param('stock_account.allow_zero_cost'):
                raise ValidationError(_("The cost of %s is currently equal to 0. Change the cost or the cost_line") % (self.product_id.display_name,))
            partner_id = (self.repair_id.partner_id and self.env['res.partner']._find_accounting_partner(self.repair_id.partner_id).id) or False
            debit_line_vals = {
                'name': self.repair_id.name,  #  as in standard when moving to production location
                'ref': self.name,
                'partner_id': partner_id,
                'product_id': cost_line.product_id.id,
                'quantity': cost_line.product_qty,
                'product_uom_id': cost_line.product_uom_id.id,
                'debit': debit_value if debit_value > 0 else 0,
                'credit': -debit_value if debit_value < 0 else 0,
                'account_id': debit_account_id,
            }
            res += [(0, 0, debit_line_vals)]
        credit_value = sum(self.mapped('cost'))
        credit_line_vals = {
            'name': self.repair_id.name,
            'ref': self.name,
            'product_id': cost_line.product_id.id,
            'quantity': cost_line.product_qty,
            'product_uom_id': cost_line.product_uom_id.id,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id
        }
        res += [(0, 0, credit_line_vals)]
        return res
