# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_return_picking_values(self, picking):
        return_type_id = picking.picking_type_id.return_picking_type_id
        return {
            'move_lines': [],
            'picking_type_id': return_type_id.id,
            'state': 'draft',
            'origin': _("Return of %s") % picking.name,
            'location_id': picking.location_dest_id.id,
            'location_dest_id':
                return_type_id and
                return_type_id.default_location_dest_id.id,
            'move_ids_without_package': [],
        }

    def _prepare_return_move_values(self, sale_order_line):
        return {
            'product_id': sale_order_line.product_id.return_product_id.id,
            'name': sale_order_line.product_id.return_product_id.name,
            'product_uom_qty': sale_order_line.product_uom_qty,
            'product_uom': sale_order_line.product_id.uom_id.id,
        }

    @api.multi
    def action_confirm(self):
        """Action Confirm.
        Create return pickings when confirming sale orders.
        """
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            picking_id = order.picking_ids and order.picking_ids[0]
            new_picking_vals = order._prepare_return_picking_values(picking_id)
            has_return = False
            for line in order.order_line:
                if line.product_id and line.product_id.returnable:
                    new_move_vals = self._prepare_return_move_values(line)
                    new_picking_vals.update = {
                        'move_ids_without_package': [(
                            0, 0, new_move_vals)]
                    }
                    has_return = True
            # if we have at least one returnable item, create the return
            if (has_return):
                new_picking = picking_id.copy(new_picking_vals)
                new_picking.message_post_with_view(
                    'mail.message_origin_link',
                    values={
                        'self': new_picking, 'origin': picking_id},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return res
