# Copyright 2018 Aleph Objects, Inc. (https://www.alephobjects.com)
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_cost_allocation_id = fields.Many2one(
        'account.account', 'Cost allocation Account', company_dependent=True,
        domain=[('deprecated', '=', False)],
        help="The expenses allocation for labor services or overhead expenses"
             " in repair orders")

    property_wip_account_id = fields.Many2one(
        'account.account', 'Work in progress Account', company_dependent=True,
        domain=[('deprecated', '=', False)],
        help="The Work in progress account for labor services or overhead "
             "while a repair order is in progress")

    @api.multi
    def get_product_accounts(self, fiscal_pos=None):
        """ Add the non material accounts related to product to the result
        of super()
        @return: dictionary which contains all needed information regarding
        labor and overhead accounts and super (income+expense accounts)
        """
        accounts = super(ProductTemplate, self).get_product_accounts(
            fiscal_pos=fiscal_pos)
        accounts.update({
            'cost_all_account': self.property_cost_allocation_id
            or self.categ_id.property_cost_allocation_id or False,
            'wip_account': (self.property_wip_account_id or
                            self.categ_id.property_wip_account_id or False),
            'stock_journal': self.categ_id.property_stock_journal_id or False,
        })
        return accounts

    def get_accounting_data_for_non_material(self, cost_type):
        """ Return the accounts and journal to use to post Journal Entries """
        accounts_data = self.get_product_accounts()
        acc_labor = accounts_data['cost_all_account'] and accounts_data[
            'cost_all_account'].id
        acc_overhead = accounts_data['wip_account'] and accounts_data[
            'wip_account'].id
        stock_journal = accounts_data['stock_journal'] and accounts_data[
            'stock_journal'].id
        if cost_type == 'labor' and not acc_labor:
            raise UserError(_(
                'Cannot find a labor account for the product %s. You '
                'must define one on the product category.') % (
                self.display_name))
        if cost_type == 'overhead' and not acc_overhead:
            raise UserError(_(
                'Cannot find an overhead account for the product %s. You '
                'must define one on the product category.') % (
                self.display_name))
        return acc_labor, acc_overhead
