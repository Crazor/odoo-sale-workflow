# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Sale Product Retunable',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Sales',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'development_status': 'Production/Stable',
    'summary': """This module allows you to set some product as returnable
                and create a reception when the sales order is confirmed.""",
    'depends': ['sale_stock'],
    'data': [
        'views/product_template_view.xml',
    ],
    'installable': True,
}
