# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import SUPERUSER_ID, api, fields, models


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    mo_exceptions = fields.Boolean(related="product_id.mrp_ok", string="MO Exceptions")
    bom_mo_exception = fields.Boolean(
        compute="_compute_bom_exception", string="BoM Exception"
    )
    mo_line_exceptions = fields.Boolean(
        compute="_compute_mo_exceptions", string="MO Line Exceptions"
    )

    @api.depends("move_raw_ids.approved_mrp_component_ok")
    def _compute_mo_exceptions(self):
        for rec in self:
            rec.mo_line_exceptions = any(
                not line.approved_mrp_component_ok for line in rec.move_raw_ids
            )

    @api.depends("bom_id")
    def _compute_bom_exception(self):
        for rec in self:
            rec.bom_mo_exception = (
                True
                if (rec.bom_id.bom_line_exceptions or rec.bom_id.bom_exceptions)
                else False
            )

    def _log_exception_activity_mrp(self, product_id):
        for order in self:
            note = self._render_product_state_excep(order, product_id)
            order.activity_schedule(
                "mail.mail_activity_data_warning",
                date.today(),
                note=note,
                user_id=order.user_id.id or SUPERUSER_ID,
            )

    def _render_product_state_excep(self, order, product_id):
        values = {"mrp_order_ref": order, "product_ref": product_id}
        return self.env.ref(
            "sale_product_approval_mrp.exception_on_mrp_production"
        )._render(values=values)


class StockMove(models.Model):
    _inherit = "stock.move"

    approved_mrp_component_ok = fields.Boolean(related="product_id.mrp_component_ok")
