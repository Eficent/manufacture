# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api
from odoo.tools import config


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def _default_active(self):
        """Needed for preserving normal flow when testing other modules."""
        res = False
        if config['test_enable']:
            res = not bool(self.env.context.get('test_mrp_bom_version'))
        return res

    def _default_state(self):
        """Needed for preserving normal flow when testing other modules."""
        res = 'draft'
        if (config['test_enable'] and
                not self.env.context.get('test_mrp_bom_version')):
            res = 'active'
        return res

    active = fields.Boolean(
        default=_default_active,
        readonly=True, states={'draft': [('readonly', False)]})
    historical_date = fields.Date(string='Historical Date', readonly=True)
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('active', 'Active'),
                   ('historical', 'Historical')], string='State',
        index=True, readonly=True, default=_default_state, copy=False)
    product_tmpl_id = fields.Many2one(
        readonly=True, states={'draft': [('readonly', False)]})
    product_id = fields.Many2one(
        readonly=True, states={'draft': [('readonly', False)]})
    product_qty = fields.Float(
        readonly=True, states={'draft': [('readonly', False)]})
    code = fields.Char(
        states={'historical': [('readonly', True)]})
    type = fields.Selection(
        states={'historical': [('readonly', True)]})
    company_id = fields.Many2one(
        states={'historical': [('readonly', True)]})
    product_uom_id = fields.Many2one(
        states={'historical': [('readonly', True)]})
    routing_id = fields.Many2one(
        readonly=True, states={'draft': [('readonly', False)]})
    bom_line_ids = fields.One2many(
        readonly=True, states={'draft': [('readonly', False)]})
    position = fields.Char(
        states={'historical': [('readonly', True)]})
    date_start = fields.Date(
        states={'historical': [('readonly', True)]})
    date_stop = fields.Date(
        states={'historical': [('readonly', True)]})
    product_rounding = fields.Float(
        states={'historical': [('readonly', True)]})
    product_efficiency = fields.Float(
        states={'historical': [('readonly', True)]})
    version = fields.Integer(states={'historical': [('readonly', True)]},
                             copy=False, default=1)
    history_head = fields.Many2one(
        'mrp.bom.history',
        'HEAD',
        compute='_compute_history_head',
        store=True,
        auto_join=True,
    )
    history_ids = fields.One2many(
        'mrp.bom.history',
        'bom_id',
        'History',
        order='create_date DESC',
        readonly=True,
    )

    @api.multi
    def button_draft(self):
        active_draft = self.env['res.config.settings']._get_parameter(
            'active.draft')
        self.write({
            'active': active_draft and active_draft.value or False,
            'state': 'draft',
        })

    @api.multi
    def button_new_version(self):
        self.ensure_one()
        new_bom = self._copy_bom()
        self.button_historical()
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form, tree',
            'view_mode': 'form',
            'res_model': 'mrp.bom',
            'res_id': new_bom.id,
            'target': 'current',
        }

    @api.multi
    def button_activate(self):
        self.write({
            'active': True,
            'state': 'active'
        })


    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Add search argument for field type if the context says so. This
        should be in old API because context argument is not the last one.
        """
        search_state = self.env.context.get('state', False)
        if search_state:
            args += [('state', '=', search_state)]
        return super(MrpBom, self).search(args, offset, limit, order, count)
