# -*- coding: utf-8 -*-
"""
    Test Product

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT
from nereid.testing import NereidTestCase
from trytond.transaction import Transaction


class TestProduct(NereidTestCase):
    """
    Test Product
    """

    def _create_product_category(self, name, vlist):
        """
        Creates a product category

        Name is mandatory while other value may be provided as keyword
        arguments

        :param name: Name of the product category
        :param vlist: List of dictionaries of values to create
        """
        Category = POOL.get('product.category')

        for values in vlist:
            values['name'] = name
        return Category.create(vlist)

    def _create_product_template(self, name, vlist, uri, uom=u'Unit'):
        """
        Create a product template with products and return its ID

        :param name: Name of the product
        :param vlist: List of dictionaries of values to create
        :param uri: uri of product template
        :param uom: Note it is the name of UOM (not symbol or code)
        """
        ProductTemplate = POOL.get('product.template')
        Uom = POOL.get('product.uom')

        for values in vlist:
            values['name'] = name
            values['default_uom'], = Uom.search([('name', '=', uom)], limit=1)
            values['sale_uom'], = Uom.search([('name', '=', uom)], limit=1)
            values['products'] = [
                ('create', [{
                    'uri': uri,
                    'displayed_on_eshop': True
                }])
            ]
        return ProductTemplate.create(vlist)

    def _create_fiscal_year(self, date=None, company=None):
        """
        Creates a fiscal year and requried sequences
        """
        FiscalYear = POOL.get('account.fiscalyear')
        Sequence = POOL.get('ir.sequence')
        SequenceStrict = POOL.get('ir.sequence.strict')
        Company = POOL.get('company.company')

        if date is None:
            date = datetime.date.today()

        if company is None:
            company, = Company.search([], limit=1)

        invoice_sequence, = SequenceStrict.create([{
            'name': '%s' % date.year,
            'code': 'account.invoice',
            'company': company,
        }])
        fiscal_year, = FiscalYear.create([{
            'name': '%s' % date.year,
            'start_date': date + relativedelta(month=1, day=1),
            'end_date': date + relativedelta(month=12, day=31),
            'company': company,
            'post_move_sequence': Sequence.create([{
                'name': '%s' % date.year,
                'code': 'account.move',
                'company': company,
            }])[0],
            'out_invoice_sequence': invoice_sequence,
            'in_invoice_sequence': invoice_sequence,
            'out_credit_note_sequence': invoice_sequence,
            'in_credit_note_sequence': invoice_sequence,
        }])
        FiscalYear.create_period([fiscal_year])
        return fiscal_year

    def _create_coa_minimal(self, company):
        """Create a minimal chart of accounts
        """
        AccountTemplate = POOL.get('account.account.template')
        Account = POOL.get('account.account')

        account_create_chart = POOL.get(
            'account.create_chart', type="wizard"
        )

        account_template, = AccountTemplate.search(
            [('parent', '=', None)]
        )

        session_id, _, _ = account_create_chart.create()
        create_chart = account_create_chart(session_id)
        create_chart.account.account_template = account_template
        create_chart.account.company = company
        create_chart.transition_create_account()

        receivable, = Account.search([
            ('kind', '=', 'receivable'),
            ('company', '=', company),
        ])
        payable, = Account.search([
            ('kind', '=', 'payable'),
            ('company', '=', company),
        ])
        create_chart.properties.company = company
        create_chart.properties.account_receivable = receivable
        create_chart.properties.account_payable = payable
        create_chart.transition_create_properties()

    def _get_account_by_kind(self, kind, company=None, silent=True):
        """Returns an account with given spec

        :param kind: receivable/payable/expense/revenue
        :param silent: dont raise error if account is not found
        """
        Account = POOL.get('account.account')
        Company = POOL.get('company.company')

        if company is None:
            company, = Company.search([], limit=1)

        accounts = Account.search([
            ('kind', '=', kind),
            ('company', '=', company)
        ], limit=1)
        if not accounts and not silent:
            raise Exception("Account not found")
        return accounts[0] if accounts else False

    def _create_payment_term(self):
        """Create a simple payment term with all advance
        """
        PaymentTerm = POOL.get('account.invoice.payment_term')

        return PaymentTerm.create([{
            'name': 'Direct',
            'lines': [('create', [{'type': 'remainder'}])]
        }])

    def setup_defaults(self):
        User = POOL.get('res.user')

        usd, = self.Currency.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }])

        with Transaction().set_context(company=None):
            party1, = self.Party.create([{
                'name': 'Openlabs',
            }])
            company, = self.Company.create([{
                'party': party1.id,
                'currency': usd.id
            }])
            party2, = self.Party.create([{
                'name': 'Guest User',
            }])
            guest_user, = self.NereidUser.create([{
                'party': party2.id,
                'display_name': 'Guest User',
                'email': 'guest@openlabs.co.in',
                'password': 'password',
                'company': company.id,
            }])
            party3, = self.Party.create([{
                'name': 'Registered User',
            }])
            self.registered_user, = self.NereidUser.create([{
                'party': party3.id,
                'display_name': 'Registered User',
                'email': 'email@example.com',
                'password': 'password',
                'company': company.id,
            }])

        self.category, = self.Category.create([{
            'name': 'CategoryA',
        }])

        User.write(
            [User(USER)], {
                'main_company': company.id,
                'company': company.id
            }
        )

        CONTEXT.update(User.get_preferences(context_only=True))
        # Create fiscal year
        self._create_fiscal_year(company=company.id)

        # Create chart of accounts
        self._create_coa_minimal(company=company.id)

        # Create website
        url_map, = self.UrlMap.search([], limit=1)
        en_us, = self.Language.search([('code', '=', 'en_US')])
        self.NereidWebsite.create([{
            'name': 'localhost',
            'url_map': url_map.id,
            'company': company.id,
            'application_user': USER,
            'default_language': en_us.id,
            'guest_user': guest_user,
        }])

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test execution.
        """
        trytond.tests.test_tryton.install_module('nereid_tutorial')

        self.Currency = POOL.get('currency.currency')
        self.Site = POOL.get('nereid.website')
        self.Product = POOL.get('product.product')
        self.Company = POOL.get('company.company')
        self.NereidUser = POOL.get('nereid.user')
        self.UrlMap = POOL.get('nereid.url_map')
        self.Language = POOL.get('ir.lang')
        self.NereidWebsite = POOL.get('nereid.website')
        self.Party = POOL.get('party.party')
        self.Category = POOL.get('product.category')
        self.Template = POOL.get('product.template')
        self.Uom = POOL.get('product.uom')
        self.AccountTemplate = POOL.get('account.account.template')
        self.Sequence = POOL.get('ir.sequence')
        self.templates = {
            'products.html': '{{ products|length}}',
        }

    def _get_template_source(self, name):
        """
        Return templates
        """
        return self.templates.get(name)

    def test_0010_product_list(self):
        """
        Get list of products
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            uom, = self.Uom.search([], limit=1)
            values1 = {
                'name': 'Saleable',
                'category': self.category.id,
                'type': 'goods',
                'salable': True,
                'sale_uom': uom.id,
                'list_price': Decimal('10'),
                'cost_price': Decimal('5'),
                'default_uom': uom.id,
                'account_expense': self._get_account_by_kind('expense').id,
                'account_revenue': self._get_account_by_kind('revenue').id,
                'products': [
                    ('create', [{
                        'description': 'Saleable',
                    }])
                ]

            }
            values2 = {
                'name': 'Not Saleable',
                'category': self.category.id,
                'type': 'goods',
                'salable': False,
                'sale_uom': uom.id,
                'list_price': Decimal('10'),
                'cost_price': Decimal('5'),
                'default_uom': uom.id,
                'account_expense': self._get_account_by_kind('expense').id,
                'account_revenue': self._get_account_by_kind('revenue').id,
                'products': [
                    ('create', [{
                        'description': 'Not Saleable',
                    }])
                ]
            }
            template1, template2 = self.Template.create([values1, values2])
            app = self.get_app()

            with app.test_client() as c:

                rv = c.get('/en_US/products')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data, '1')


def suite():
    "Test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestProduct)
    )
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
