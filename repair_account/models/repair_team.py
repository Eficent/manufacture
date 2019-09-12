# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
UNIT = dp.get_precision('Product Price')


class RepairTeam(models.Model):
    _inherit = 'repair.team'

    labor_standard_cost = fields.Float(
        string='Labor Repair Standard cost',
        digits=UNIT)
    overhead_standard_cost = fields.Float(
        string='Overhead repair Standard cost',
        digits=UNIT)
    labor_allocation_account_id = fields.Many2one(
        'account.account', 'Labor allocation Account', company_dependent=True,
        domain=[('deprecated', '=', False)],
        help="The expenses allocation for labor in repair orders")
    overhead_allocation_account_id = fields.Many2one(
        'account.account', 'Overhead allocation Account',
        company_dependent=True,
        domain=[('deprecated', '=', False)],
        help="The expenses allocation for labor in repair orders")
    journal_id = fields.Many2one('account.journal', required=True)
