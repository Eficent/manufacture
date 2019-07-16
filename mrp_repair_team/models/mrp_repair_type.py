# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpRepairType(models.Model):
    _name = 'mrp.repair.type'

    name = fields.Char()
    default_raw_material_prod_location_id = fields.Many2one(
        'stock.location',
        required=True,
        string="Location to send the consumed products",
        help="It is a production location and determines the account hit"
             "when consuming")
    invoice_method = fields.Selection([
        ("none", "No Invoice"),
        ("b4repair", "Before Repair"),
        ("after_repair", "After Repair")], string="Invoice Method",
        default='none',
        help='Selecting \'Before Repair\' or \'After Repair\' will allow you'
             ' to generate invoice before or after the repair is done'
             ' respectively. \'No invoice\' means you don\'t want to'
             ' generate invoice for this repair order.')
