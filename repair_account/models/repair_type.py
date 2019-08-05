# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class RepairType(models.Model):
    _inherit = 'repair.type'

    journal_id = fields.Many2one('account.journal', required=True)
    wip_account_id = fields.Many2one(
        'account.account', 'Repair Work in progress account',
        company_dependent=True,
        domain=[('deprecated', '=', False)],
        help="The Work in progress account repairs")

    refurbish_location_id = fields.Many2one(
        'stock.location', "Force Refurbish location on repair order")
