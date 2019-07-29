# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    user_id = fields.Many2one(
        'res.users', 'Responsible', default=lambda self: self._uid
    )
