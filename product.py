# -*- coding: utf-8 -*-
"""
    product

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta
from nereid import render_template

__metaclass__ = PoolMeta


class Product:
    "Extend product model"
    __name__ = 'product.product'

    @classmethod
    def render_list(cls):
        """
        Render a list of products
        """
        products = cls.search([('salable', '=', True)])
        return render_template('products.html', products=products)
