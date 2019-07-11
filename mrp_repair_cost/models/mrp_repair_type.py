# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpRepairType(models.Model):
    _inherit = 'mrp.repair.type'

    journal_id = fields.Many2one('account.journal', required=True)
    default_labor_product_id = fields.Many2one('product.product')
    default_oh_product_id = fields.Many2one('product.product')
