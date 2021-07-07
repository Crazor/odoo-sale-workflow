# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import SUPERUSER_ID, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    approved_sale = fields.Boolean(
        related="product_id.sale_ok",
        string="Approved for Sale",
        store=True,
        default=True,
    )


class SaleOrder(models.Model):
    _inherit = "sale.order"

    exceptions = fields.Boolean(
        compute="_compute_exceptions",
        string="Exception",
    )

    def _compute_exceptions(self):
        self.exceptions = False
        if any(not line.approved_sale for line in self.order_line):
            self.exceptions = True

    def _log_exception_activity_sale(self, render_method, documents, product_id):
        for order in documents:
            note = render_method(order, product_id)
            order.activity_schedule(
                "mail.mail_activity_data_warning",
                date.today(),
                note=note,
                user_id=order.user_id.id or SUPERUSER_ID,
            )

    def _log_product_state(self, documents, product_id, cancel=False):
        def _render_product_state_excep(order, product_id):
            values = {"sale_order_ref": order, "product_ref": product_id}
            return self.env.ref("sale_product_approval.exception_on_product")._render(
                values=values
            )

        self.env["sale.order"]._log_exception_activity_sale(
            _render_product_state_excep, documents, product_id
        )
