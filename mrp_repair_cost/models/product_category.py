# Copyright 2018 Aleph Objects, Inc. (https://www.alephobjects.com)
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_cost_allocation_id = fields.Many2one(
        'account.account', 'Cost Allocation Account', company_dependent=True,
        domain=[('deprecated', '=', False)],
        help="The expenses allocation for labor services or overhead expenses"
             " in repair orders")

    property_wip_account_id = fields.Many2one(
        'account.account', 'Work in progress  Account', company_dependent=True,
        domain=[('deprecated', '=', False)],
        help="The Work in progress account for labor services or overhead "
             "while a repair order is in progress")
