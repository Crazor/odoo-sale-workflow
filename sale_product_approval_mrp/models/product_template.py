# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mrp_ok = fields.Boolean(
        string="Can be Manufactured",
        compute="_compute_mrp_ok_product",
        default=False,
        store=True,
    )
    mrp_component_ok = fields.Boolean(
        string="Can be a Component on a Manufacturing Order",
        compute="_compute_mrp_component_ok_product",
        default=False,
        store=True,
    )
    bom_ok = fields.Boolean(
        string="Can be on BoM",
        compute="_compute_bom_ok_product",
        default=False,
        store=True,
    )
    candidate_manufacture = fields.Boolean(
        string="Candidate to be Manufactured", default=True
    )
    candidate_component_manufacture = fields.Boolean(
        string="Candidate to be a Component on Manufacturing Orders", default=True
    )
    candidate_bom = fields.Boolean(string="Candidate to be on BoM", default=True)

    @api.depends("candidate_manufacture", "product_state_id.approved_mrp")
    def _compute_mrp_ok_product(self):
        for product in self:
            if product.product_state_id:
                product.mrp_ok = (
                    product.candidate_manufacture
                    and product.product_state_id.approved_mrp
                )
                if not product.mrp_ok:
                    order_ids = self.env["mrp.production"].search(
                        [
                            ("product_id", "in", product.product_variant_ids.ids),
                            ("state", "in", ["draft", "confirmed", "progress"]),
                            ("mo_exceptions", "=", True),
                        ]
                    )
                    order_ids._log_exception_activity_mrp(product)

    @api.depends(
        "candidate_component_manufacture", "product_state_id.approved_component_mrp"
    )
    def _compute_mrp_component_ok_product(self):
        for product in self:
            if product.product_state_id:
                product.mrp_component_ok = (
                    product.candidate_component_manufacture
                    and product.product_state_id.approved_component_mrp
                )
                if not product.mrp_component_ok:
                    order_ids = (
                        self.env["stock.move"]
                        .search(
                            [
                                ("product_id", "in", product.product_variant_ids.ids),
                                (
                                    "raw_material_production_id.state",
                                    "in",
                                    ["draft", "confirmed", "progress"],
                                ),
                                ("approved_mrp_component_ok", "=", True),
                            ]
                        )
                        .mapped("raw_material_production_id")
                    )
                    order_ids._log_exception_activity_mrp(product)

    @api.depends("candidate_bom", "product_state_id.approved_bom")
    def _compute_bom_ok_product(self):
        for product in self:
            if product.product_state_id:
                product.bom_ok = (
                    product.candidate_bom and product.product_state_id.approved_bom
                )
