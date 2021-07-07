# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_ok = fields.Boolean("Can be Sold", default=False)
    candidate_sale = fields.Boolean(
        string="Candidate to be Sold",
    )

    @api.onchange("product_state_id")
    def _onchange_product_state(self):
        self.sale_ok = False
        if self.product_state_id.approved_sale and self.candidate_sale:
            self.sale_ok = True

    @api.model
    def _get_default_product_state_id(self):
        return self.env.ref(
            "product_state.product_state_draft", raise_if_not_found=False
        )


class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if not vals.get("sale_ok"):
            order_ids = (
                self.env["sale.order.line"]
                .search(
                    [("product_id", "=", self.id), ("state", "in", ["draft", "sent"])]
                )
                .mapped("order_id")
            )
            self.env["sale.order"]._log_product_state(order_ids, self)
        return res

    @api.onchange("product_state_id")
    def _onchange_product_state(self):
        self.sale_ok = False
        if self.product_state_id.approved_sale and self.candidate_sale:
            self.sale_ok = True
