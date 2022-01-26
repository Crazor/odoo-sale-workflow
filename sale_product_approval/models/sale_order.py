# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError


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

    exceptions_sale_approval = fields.Boolean(
        compute="_compute_exceptions", string="Exception", default=False
    )
    override_exception = fields.Boolean("Override Exception", default=False)

    @api.depends("order_line.approved_sale")
    def _compute_exceptions(self):
        self.exceptions_sale_approval = any(
            not line.approved_sale
            for line in self.order_line.filtered(lambda x: not x.display_type)
        )

    def _log_exception_activity_sale(self, product_id):
        for order in self:
            note = self._render_product_state_excep(order, product_id)
            order.activity_schedule(
                "mail.mail_activity_data_warning",
                date.today(),
                note=note,
                user_id=order.user_id.id or SUPERUSER_ID,
            )

    def _render_product_state_excep(self, order, product_id):
        values = {"sale_order_ref": order, "product_ref": product_id}
        return self.env.ref("sale_product_approval.exception_on_product")._render(
            values=values
        )

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for sale in self:
            if sale.exceptions_sale_approval and not sale.override_exception:
                raise UserError(
                    _(
                        "You can not confirm this sale order "
                        "because some products are not sellable in this order."
                    )
                )
        return res
