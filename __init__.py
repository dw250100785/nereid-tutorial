# -*- coding: utf-8 -*-
"""
    __init__


    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from product import Product


def register():
    Pool.register(
        Product,
        module='nereid_tutorial', type_='model'
    )
