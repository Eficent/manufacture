# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.one
    def _get_old_versions(self):
        parent = self.parent_bom
        old_version = self.env['mrp.bom']
        while parent:
            old_version += parent
            parent = parent.parent_bom
        self.old_versions = old_version

    def compute_valid(self):
        dt = fields.Datetime.now()
        for rec in self:
            if rec.date_start and rec.date_stop and \
                    (dt < rec.date_stop and dt > rec.date_start):
                rec.valid = True
            else:
                rec.valid = False

    valid = fields.Boolean(compute='compute_valid')
    bom_type = fields.Selection(
        selection=[('primary', 'Primary'), ('alternate', 'Alternate')],
        string='BOM Type', help='A normal BOM is primary, and alternate is'
                                ' a prototype',
        index=True, default='primary')
    date_start = fields.Date(string='Start Date',
                             help="BOM valid from this date")
    date_stop = fields.Date(string='End Date',
                            help="BOM valid until this date")
    version = fields.Integer('BOM version', default=1)
    parent_bom = fields.Many2one(
        comodel_name='mrp.bom', string='Parent BoM')
    old_versions = fields.Many2many(
        comodel_name='mrp.bom', string='Old Versions',
        compute='_get_old_versions')

    @api.multi
    def copy(self):
        self.ensure_one()
        new_bom = self.copy()
        self.date_stop = fields.Datetime.now()
        new_bom.date_start = fields.Datetime.now()
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form, tree',
            'view_mode': 'form',
            'res_model': 'mrp.bom',
            'res_id': new_bom.id,
            'target': 'current',
        }

    @api.model
    def create(self, vals):
        if vals['product_tmpl_id']:
            boms = self.search(
                [('product_tmpl_id', '=', vals['product_tmpl_id'])],
                order='version desc', limit=1)
            if boms:
                vals['version'] = boms.version+1
        return super(MrpBom, self).create(vals)

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            boms = self.search(
                [('product_tmpl_id', '=', self.product_tmpl_id.id)],
                order='version desc', limit=1)
            if boms:
                self.version = boms.version + 1
