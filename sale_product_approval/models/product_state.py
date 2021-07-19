# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductState(models.Model):
    _inherit = "product.state"

    approved_sale = fields.Boolean(string="Approved to be Sold", default=True)

    def write(self, vals):
        res = super(ProductState, self).write(vals)
        if vals.get("approved_sale") or vals.get("approved_sale") is False:
            product_ids = self.env["product.product"].search(
                [("product_state_id", "=", self.id), ("candidate_sale", "=", True)]
            )
            for product in product_ids:
                if vals.get("approved_sale"):
                    product.sale_ok = True
                else:
                    product.sale_ok = False
        return res
