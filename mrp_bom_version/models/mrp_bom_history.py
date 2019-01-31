from odoo import api, fields, models


class DocumentPageHistory(models.Model):
    """This model is necessary to manage a document history."""

    _name = "mrp.bom.history"
    _description = "Document Page History"
    _order = 'id DESC'

    bom_id = fields.Many2one('mrp.bom', 'BOM', ondelete='cascade')
    name = fields.Char(index=True)
    date = fields.Date
    rem_bom_line_ids = fields.Many2many('mrp.bom.line')
    new_bom_line_ids = fields.Many2many('mrp.bom.line')
