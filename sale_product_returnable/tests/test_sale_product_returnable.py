# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo.tests import TransactionCase


class TestSaleProductReturnable(TransactionCase):

    def setUp(self):
        super(TestSaleProductReturnable, self).setUp()
        self.tax_model = self.env['account.tax']
        self.SaleOrder = self.env['sale.order']

        self.partner_18 = self.env.ref('base.res_partner_18')
        self.pricelist = self.env.ref('product.list0')
        self.product_10 = self.env.ref('product.product_product_10')
        self.product_4d = self.env.ref('product.product_product_4d')
        self.product_uom_unit = self.env.ref('uom.product_uom_unit')

    def test_action_confirm(self):
        self.product_10.returned = True
        self.product_10.returned_product_id = self.product_4d.id
        # Create sale order
        self.percent_tax = self.tax_model.create({
            'name': "Percent tax",
            'amount_type': 'percent',
            'amount': 10,
            'sequence': 3,
        })
        # self.normal_delivery.product_id.taxes_id = self.percent_tax
        self.sale = self.SaleOrder.create({
            'partner_id': self.partner_18.id,
            'partner_invoice_id': self.partner_18.id,
            'partner_shipping_id': self.partner_18.id,
            'pricelist_id': self.pricelist.id,
            'order_line': [(0, 0, {
                'name': 'PC Assamble + 2GB RAM',
                'product_id': self.product_10.id,
                'product_uom_qty': 1,
                'product_uom': self.product_uom_unit.id,
                'price_unit': 750.00,
                'tax_id': [(4, self.percent_tax.id, 0)]
            })],
        })

        self.sale.action_confirm()
        self.assertTrue(self.sale.state == 'sale')
