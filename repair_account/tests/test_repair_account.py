# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestRepairAccount(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestRepairAccount, self).setUp(*args, **kwargs)
        self.repair_obj = self.env['repair.order']
        self.repair_line_obj = self.env['repair.line']
        self.product_obj = self.env['product.product']
        self.location_obj = self.env['stock.location']
        self.move_obj = self.env['stock.move']
        self.aml_obj = self.env['account.move.line']
        self.am_obj = self.env['account.move']

        self.stock_location_stock = self.env.ref('stock.stock_location_stock')
        self.company = self.env.ref('base.main_company')
        self.stock_location_stock.company_id = self.company.id
        self.stock_location_rma_internal = self.stock_location_stock.copy()
        self.stock_location_rma_internal.name = 'RMA internal'
        self.stock_location_rma_external = self.stock_location_stock.copy()
        self.stock_location_rma_external.name = 'RMA External'
        self.stock_location_rma_external.company_id = False
        self.stock_location_rma_external.usage = 'customer'

        self.stock_location_customers = self.env.ref(
            'stock.stock_location_customers')
        self.warehouse = self.env.ref('stock.warehouse0')

        self.stock_location_repair = self.env.ref(
            'repair_account.stock_location_repair')
        self.stock_location_repair_warranty = self.env.ref(
            'repair_account.stock_location_repair_warranty')
        self.stock_location_repair_internal = self.env.ref(
            'repair_account.stock_location_repair_internal')
        self.stock_location_repair_refurbish = self.env.ref(
            'repair_account.stock_location_repair_refurbish')
        self.refurbish_location = self.env.ref(
            'repair_refurbish.stock_location_refurbish')
        self.repair_team = self.env.ref(
            'repair_account.repair_team_dep1')
        self.default_raw_material_location_id = \
            self.repair_team.default_raw_material_location_id

        self.repair_type_no_warranty = self.env.ref(
            'repair_account.repair_type_no_warranty')
        self.repair_type_warranty = self.env.ref(
            'repair_account.repair_type_warranty')
        self.repair_type_internal = self.env.ref(
            'repair_account.repair_type_internal')
        self.repair_type_refurbish = self.env.ref(
            'repair_account.repair_type_refurbish')

        self.stock_location_repair_warranty = self.env.ref(
            'repair_account.stock_location_repair_warranty')
        self.stock_location_repair_internal = self.env.ref(
            'repair_account.stock_location_repair_internal')
        self.stock_location_repair_refurbish = self.env.ref(
            'repair_account.stock_location_repair_refurbish')

        self.refurbish_product = self.product_obj.create({
            'name': 'Refurbished Awesome Screen',
            'type': 'product',
        })
        self.refurbish_product.product_tmpl_id.standard_price = 21
        self.refurbish_product.categ_id.property_valuation = 'real_time'

        self.product1 = self.product_obj.create({
            'name': 'Awesome Screen',
            'type': 'product',
            'refurbish_product_id': self.refurbish_product.id,
        })
        self.product1.product_tmpl_id.standard_price = 10
        self.product1.categ_id.property_valuation = 'real_time'
        self.product2 = self.product_obj.create({
            'name': 'Not Awesome Screen',
            'type': 'product',
        })
        self.product2.product_tmpl_id.standard_price = 10
        self.product2.categ_id.property_valuation = 'real_time'
        self.product2.categ_id.journal_id = self.env['account.journal'].search(
            [('type', '=', 'general')])[0]
        self.material = self.product_obj.create({
            'name': 'Materials',
            'type': 'product',
        })


        self.material.product_tmpl_id.standard_price = 10
        self.material.categ_id.property_valuation = 'real_time'
        self._update_product_qty(
            self.product2, self.stock_location_stock, 10.0)

        self.env.user.repair_team_id = self.repair_team.id

        self.cogr_acc = self.env.ref(
            'repair_account.demo_account_cogr')
        self.uwr_acc = self.env.ref(
            'repair_account.demo_account_uwr')
        self.off_acc = self.env.ref(
            'repair_account.demo_account_ofs')
        self.refurbish_acc = self.env.ref(
            'repair_account.demo_account_refr')
        self.labor_all_acc = self.env.ref(
            'repair_account.demo_account_labor_all')
        self.oh_all_acc = self.env.ref(
            'repair_account.demo_account_overhead_all')

        self.stock_location_repair.valuation_in_account_id = self.cogr_acc.id,
        self.stock_location_repair.valuation_out_account_id = self.cogr_acc.id

        self.stock_location_repair_warranty.valuation_in_account_id = \
            self.uwr_acc.id
        self.stock_location_repair_warranty.valuation_out_account_id = \
            self.uwr_acc.id

        self.stock_location_repair_internal.valuation_in_account_id = \
            self.off_acc.id
        self.stock_location_repair_internal.valuation_out_account_id = \
            self.off_acc.id

        self.stock_location_repair_refurbish.valuation_in_account_id = \
            self.refurbish_acc.id
        self.stock_location_repair_refurbish.valuation_out_account_id = \
            self.refurbish_acc.id

    def create_stock_move(self, product, qty, loc1, loc2):
        """Create a Stock Move."""
        move = self.env['stock.move'].create({
            'name': 'Reordering Product',
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': qty,
            'location_id': loc1.id,
            'location_dest_id': loc2.id
        })
        move._action_confirm()
        move._action_assign()
        move.move_line_ids[0].qty_done = 1.0
        move._action_done()
        return move

    def _update_product_qty(self, product, location, quantity):
        product_qty = self.env['stock.change.product.qty'].create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': quantity,
        })
        product_qty.change_product_qty()
        return product_qty

    def test_01_repair_no_warranty(self):
        """Accounting entries for a reparation with no warranty """
        # move first to repair location
        move = self.create_stock_move(
            self.product2, 1.0, self.stock_location_customers,
            self.stock_location_rma_external)
        move_aml = self.am_obj.search([('stock_move_id', '=', move.id)])
        self.assertEqual(move_aml, self.am_obj)
        repair = self.repair_obj.create({
            'product_id': self.product2.id,
            'product_qty': 1.0,
            'type_id': self.repair_type_no_warranty.id,
            'product_uom': self.product2.uom_id.id,
            'location_id': self.stock_location_rma_external.id,
            'location_dest_id': self.stock_location_rma_external.id,
        })
        line = self.repair_line_obj.create({
            'name': 'consume stuff to repair',
            'repair_id': repair.id,
            'type': 'add',
            'product_id': self.material.id,
            'product_uom': self.material.uom_id.id,
            'product_uom_qty': 1.0,
            'location_id': self.stock_location_stock.id,
            'location_dest_id': self.stock_location_stock.id,
            'price_unit': 10.0
        })
        line.onchange_product_id()
        line.repair_id.onchange_type_id()
        line.repair_id.onchange_team_id()
        self.assertEqual(line.location_id,
                         self.repair_team.default_raw_material_location_id)
        self.assertEqual(line.location_dest_id,
                         self.repair_type_no_warranty.
                         default_raw_material_prod_location_id)
        # Complete repair:
        repair.action_repair_ready()
        repair.action_repair_start()
        repair.action_repair_end()

        # check stock moves
        moves = self.move_obj.search([('reference', '=', repair.name)])
        for m in moves:
            self.assertEqual(m.state, 'done')
            if m.product_id == self.product2:
                self.assertEqual(m.location_id,
                                 self.stock_location_rma_external)
                self.assertEqual(m.location_dest_id,
                                 self.stock_location_rma_external)
            elif m.product_id == self.material:
                self.assertEqual(m.location_id,
                                 self.default_raw_material_location_id)
                self.assertEqual(m.location_dest_id,
                                 self.stock_location_repair)
            else:
                self.assertTrue(False, "Unexpected move.")

        # check journal entries
        aml = self.aml_obj.search([('name', '=', repair.name)])
        self.assertEqual(len(aml), 6)
        # 1 cogr and inventory +  1 cogr and labor allocation + 1 cogr
        # and overhead allocation
        amlr = aml.filtered(lambda a: a.account_id == self.cogr_acc)
        self.assertEqual(len(amlr), 3)
        self.assertEqual(sum(amlr.mapped('debit')), 21)

        amlinv = aml.filtered(
            lambda a: a.account_id ==
            self.material.categ_id.
            property_stock_valuation_account_id)
        self.assertEqual(len(amlinv), 1)
        self.assertEqual(sum(amlinv.mapped('credit')), 10)

        amllab = aml.filtered(lambda a: a.account_id == self.labor_all_acc)
        self.assertEqual(len(amllab), 1)
        self.assertEqual(sum(amllab.mapped('credit')), 10)

        amloh = aml.filtered(lambda a: a.account_id == self.oh_all_acc)
        self.assertEqual(len(amloh), 1)
        self.assertEqual(sum(amloh.mapped('credit')), 1)
        # move back to customers
        move = self.create_stock_move(
            self.product2, 1.0, self.stock_location_rma_external,
            self.stock_location_customers)
        move_aml = self.am_obj.search([('stock_move_id', '=', move.id)])
        self.assertEqual(move_aml, self.am_obj)

    def test_02_repair_under_warranty(self):
        """Accounting entries for a reparation with warranty """
        # move first to repair location
        self.create_stock_move(
            self.product2, 1.0, self.stock_location_customers,
            self.stock_location_rma_external)

        repair = self.repair_obj.create({
            'product_id': self.product2.id,
            'product_qty': 1.0,
            'type_id': self.repair_type_warranty.id,
            'product_uom': self.product2.uom_id.id,
            'location_id': self.stock_location_rma_external.id,
            'location_dest_id': self.stock_location_rma_external.id,
        })
        line = self.repair_line_obj.create({
            'name': 'consume stuff to repair',
            'repair_id': repair.id,
            'type': 'add',
            'product_id': self.material.id,
            'product_uom': self.material.uom_id.id,
            'product_uom_qty': 1.0,
            'location_id': self.stock_location_stock.id,
            'location_dest_id': self.stock_location_stock.id,
            'price_unit': 10.0
        })
        line.onchange_product_id()
        line.repair_id.onchange_type_id()
        line.repair_id.onchange_team_id()
        self.assertEqual(line.location_id,
                         self.repair_team.default_raw_material_location_id)
        self.assertEqual(line.location_dest_id,
                         self.repair_type_warranty.
                         default_raw_material_prod_location_id)
        # Complete repair:
        repair.action_repair_ready()
        repair.action_repair_start()
        repair.action_repair_end()

        # check stock moves
        moves = self.move_obj.search([('reference', '=', repair.name)])
        for m in moves:
            self.assertEqual(m.state, 'done')
            if m.product_id == self.product2:
                self.assertEqual(m.location_id,
                                 self.stock_location_rma_external)
                self.assertEqual(m.location_dest_id,
                                 self.stock_location_rma_external)
            elif m.product_id == self.material:
                self.assertEqual(m.location_id,
                                 self.default_raw_material_location_id)
                self.assertEqual(m.location_dest_id,
                                 self.stock_location_repair_warranty)
            else:
                self.assertTrue(False, "Unexpected move.")

        # check journal entries
        aml = self.aml_obj.search([('name', '=', repair.name)])
        self.assertEqual(len(aml), 6)
        # 1 cogr and inventory +  1 cogr and labor allocation + 1 cogr and overhead allocation
        amlr = aml.filtered(lambda a: a.account_id == self.uwr_acc)
        self.assertEqual(len(amlr), 3)
        self.assertEqual(sum(amlr.mapped('debit')), 21)

        amlinv = aml.filtered(
            lambda a: a.account_id ==
            self.material.categ_id.
            property_stock_valuation_account_id)
        self.assertEqual(len(amlinv), 1)
        self.assertEqual(sum(amlinv.mapped('credit')), 10)

        amllab = aml.filtered(lambda a: a.account_id == self.labor_all_acc)
        self.assertEqual(len(amllab), 1)
        self.assertEqual(sum(amllab.mapped('credit')), 10)

        amloh = aml.filtered(lambda a: a.account_id == self.oh_all_acc)
        self.assertEqual(len(amloh), 1)
        self.assertEqual(sum(amloh.mapped('credit')), 1)
        # move back to customers
        self.create_stock_move(
            self.product2, 1.0, self.stock_location_rma_external,
            self.stock_location_customers)

    def test_03_repair_under_internal(self):
        """Accounting entries for internal reparation """
        # move first to repair location
        move = self.create_stock_move(
            self.product2, 1.0, self.stock_location_stock,
            self.stock_location_rma_internal)
        move_aml = self.am_obj.search([('stock_move_id', '=', move.id)])
        self.assertEqual(move_aml, self.am_obj)
        repair = self.repair_obj.create({
            'product_id': self.product2.id,
            'product_qty': 1.0,
            'type_id': self.repair_type_internal.id,
            'product_uom': self.product2.uom_id.id,
            'location_id': self.stock_location_rma_internal.id,
            'location_dest_id': self.stock_location_rma_internal.id,
        })
        line = self.repair_line_obj.create({
            'name': 'consume stuff to repair',
            'repair_id': repair.id,
            'type': 'add',
            'product_id': self.material.id,
            'product_uom': self.material.uom_id.id,
            'product_uom_qty': 1.0,
            'location_id': self.stock_location_stock.id,
            'location_dest_id': self.stock_location_stock.id,
            'price_unit': 10.0
        })
        line.onchange_product_id()
        line.repair_id.onchange_type_id()
        line.repair_id.onchange_team_id()
        self.assertEqual(line.location_id,
                         self.repair_team.default_raw_material_location_id)
        self.assertEqual(line.location_dest_id,
                         self.repair_type_internal.
                         default_raw_material_prod_location_id)
        # Complete repair:
        repair.action_repair_ready()
        repair.action_repair_start()
        repair.action_repair_end()

        # check stock moves
        moves = self.move_obj.search([('reference', '=', repair.name)])
        for m in moves:
            self.assertEqual(m.state, 'done')
            if m.product_id == self.product2:
                self.assertEqual(m.location_id,
                                 self.stock_location_rma_internal)
                self.assertEqual(m.location_dest_id,
                                 self.stock_location_rma_internal)
            elif m.product_id == self.material:
                self.assertEqual(m.location_id,
                                 self.default_raw_material_location_id)
                self.assertEqual(m.location_dest_id,
                                 self.stock_location_repair_internal)
            else:
                self.assertTrue(False, "Unexpected move.")

        # check journal entries
        aml = self.aml_obj.search([('name', '=', repair.name)])
        self.assertEqual(len(aml), 6)
        # 1 cogr and inventory +  1 cogr and labor allocation +
        # 1 cogr and overhead allocation
        amlr = aml.filtered(lambda a: a.account_id == self.off_acc)
        self.assertEqual(len(amlr), 3)
        self.assertEqual(sum(amlr.mapped('debit')), 21)

        amlinv = aml.filtered(
            lambda a: a.account_id ==
            self.material.categ_id.
            property_stock_valuation_account_id)
        self.assertEqual(len(amlinv), 1)
        self.assertEqual(sum(amlinv.mapped('credit')), 10)

        amllab = aml.filtered(lambda a: a.account_id == self.labor_all_acc)
        self.assertEqual(len(amllab), 1)
        self.assertEqual(sum(amllab.mapped('credit')), 10)

        amloh = aml.filtered(lambda a: a.account_id == self.oh_all_acc)
        self.assertEqual(len(amloh), 1)
        self.assertEqual(sum(amloh.mapped('credit')), 1)
        # move first to general stock
        move = self.create_stock_move(
            self.product2, 1.0, self.stock_location_rma_internal,
            self.stock_location_stock)
        move_aml = self.am_obj.search([('stock_move_id', '=', move.id)])
        self.assertEqual(move_aml, self.am_obj)

    def test_04_repair_refusrbish(self):
        """Accounting entries for refursbish """

        # move first to repair location
        move = self.create_stock_move(
            self.product1, 1.0, self.stock_location_customers,
            self.stock_location_rma_internal)
        move_aml = self.am_obj.search([('stock_move_id', '=', move.id)])
        self.assertEqual(sum(move_aml.mapped('line_ids.debit')), 10.0)

        repair = self.repair_obj.create({
            'product_id': self.product1.id,
            'product_qty': 1.0,
            'type_id': self.repair_type_refurbish.id,
            'product_uom': self.product1.uom_id.id,
            'location_id': self.stock_location_rma_internal.id,
            'location_dest_id': self.stock_location_rma_internal.id,
            'to_refurbish': True,
        })
        line = self.repair_line_obj.create({
            'name': 'consume stuff to repair',
            'repair_id': repair.id,
            'type': 'add',
            'product_id': self.material.id,
            'product_uom': self.material.uom_id.id,
            'product_uom_qty': 1.0,
            'location_id': self.stock_location_stock.id,
            'location_dest_id': self.stock_location_stock.id,
            'price_unit': 10.0
        })
        repair._onchange_to_refurbish()
        line.onchange_product_id()
        line.repair_id.onchange_type_id()
        line.repair_id.onchange_team_id()
        self.assertEqual(line.location_id,
                         self.repair_team.default_raw_material_location_id)
        self.assertEqual(line.location_dest_id,
                         self.repair_type_refurbish.
                         default_raw_material_prod_location_id)
        # Complete repair:
        repair.action_repair_ready()
        repair.action_repair_start()
        repair.action_repair_end()

        # check stock moves
        moves = self.move_obj.search([('reference', '=', repair.name)])
        for m in moves:
            self.assertEqual(m.state, 'done')
            if m.product_id == self.product1:
                self.assertEqual(m.location_id,
                                 self.stock_location_rma_internal)
                self.assertEqual(m.location_dest_id,
                                 self.stock_location_repair_refurbish)
            elif m.product_id == self.refurbish_product:
                self.assertEqual(m.location_id,
                                 self.stock_location_repair_refurbish)
                self.assertEqual(m.location_dest_id,
                                 self.stock_location_rma_internal)
            elif m.product_id == self.material:
                self.assertEqual(m.location_id,
                                 self.default_raw_material_location_id)
                self.assertEqual(m.location_dest_id,
                                 self.stock_location_repair_refurbish)
            else:
                self.assertTrue(False, "Unexpected move.")

        # check journal entries
        aml = self.aml_obj.search([('name', '=', repair.name)])
        self.assertEqual(len(aml), 10)
        # 3+2 refusrbish +  1 cogr and labor allocation +
        # 1 cogr and overhead allocation
        amlr = aml.filtered(lambda a: a.account_id == self.refurbish_acc)
        self.assertEqual(len(amlr), 5)
        self.assertEqual(sum(amlr.mapped('debit')), 31)
        self.assertEqual(sum(amlr.mapped('credit')), 21)

        amlinv = aml.filtered(
            lambda a: a.account_id ==
            self.material.categ_id.
            property_stock_valuation_account_id)
        self.assertEqual(len(amlinv), 3)
        self.assertEqual(sum(amlinv.mapped('credit')), 20)
        # lost product to repair + original product
        self.assertEqual(sum(amlinv.mapped('debit')), 21)

        amllab = aml.filtered(lambda a: a.account_id == self.labor_all_acc)
        self.assertEqual(len(amllab), 1)
        self.assertEqual(sum(amllab.mapped('credit')), 10)

        amloh = aml.filtered(lambda a: a.account_id == self.oh_all_acc)
        self.assertEqual(len(amloh), 1)
        self.assertEqual(sum(amloh.mapped('credit')), 1)

        # no move back, the repair order moves the refurbished product
