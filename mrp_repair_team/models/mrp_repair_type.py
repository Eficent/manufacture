# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpRepairType(models.Model):
    _name = 'mrp.repair.type'

    name = fields.Char()
    default_raw_material_prod_location_id = fields.Many2one('stock.location',
                                                            required=True)
    journal_id = fields.Many2one('account.journal', required=True)
    debit_account_id = fields.Many2one('account.account', required=True)
    # credit for inventory determined by the location not here, only one account specified above
    credit_labor_account_id = fields.Many2one('account.account', required=True)
    credit_overhead_account_id = fields.Many2one('account.account', required=True)
