#!/bin/env python3
from datetime import datetime
import unittest

from selenium.webdriver.firefox.service import Service
from splinter import Browser

from store.data import *
import test_helpers as helpers


browser = None


def setUpModule():
    global browser
    browser = Browser("firefox", service=Service())
    browser.visit("http://127.0.0.1:5000/store")


def tearDownModule():
    global browser
    if browser is not None:
        browser.quit()


class BaseTestClass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global browser
        cls.browser = browser
        cls.products = helpers.get_products()


class CartPageTests(BaseTestClass):
    def setUp(self):
        """This code runs before each test method."""
        super().setUp()
        helpers.clean_cart()
        self.page = "http://127.0.0.1:5000/cart/"
        self.cart = Cart.select().order_by(-Cart.id).first()

    def test_empty_cart(self):
        self.browser.visit(self.page)
        self.assertTrue(browser.is_text_present("Looks like your cart is empty."))

    def test_nonempty_cart(self):
        # add first 3 products to the cart instance
        products = self.products[:3]
        helpers.load_cart(self.cart.id, products)
        self.browser.visit(self.page)

        # verify that the 3 products are being displayed on the page

        self.fail("Implement test")

    def test_deleting_from_cart(self):
        # add first 3 products to the cart instance
        products = self.products[:3]
        helpers.load_cart(self.cart.id, products)
        self.browser.visit(self.page)

        # click remove icon
        # check that product isn't on page any more
        # check that we got a success message

        self.fail("Implement test")


class ProductPageTests(BaseTestClass):
    def setUp(self):
        super().setUp()
        helpers.clean_cart()
        self.page = "http://127.0.0.1:5000/item/"
        self.product = self.products[0]
        self.product_page = f"{self.page}/{self.product.slug}"

    def test_invalid_product_name_returns_error(self):
        """Invalid product should redirect to store and present error"""
        self.browser.visit(f"{self.page}/foo-bar-baz")

        self.assertEqual(self.browser.url, "http://127.0.0.1:5000/store")
        self.assertTrue(self.browser.is_text_present("Invalid product selected"))

    def test_deleted_product_returns_error(self):
        """Deleted product should redirect to store and present error"""
        product = Product.select().where(Product.id == self.product).for_update().get()
        product.deleted = datetime.now()
        product.save()

        try:
            self.browser.visit(self.product_page)
            self.assertEqual(self.browser.url, "http://127.0.0.1:5000/store")
            self.assertTrue(self.browser.is_text_present("Invalid product selected"))
        finally:
            product.deleted = None
            product.save()

    def test_displays_product_data(self):
        self.browser.visit(self.product_page)

        # description converts newlines to paragraphs or break tags
        # so only check that the text exists
        for paragraph in self.product.description.split("\n"):
            self.assertTrue(browser.is_text_present(paragraph.strip()))

    def test_reviews_are_displayed(self):
        product = next(
            (p for p in self.products if p.deleted is None and len(p.reviews) > 0)
        )
        browser.visit(f"{self.page}/{product.slug}")

        for i, review in enumerate(product.reviews):
            if i == 10:
                break
            expected_text = review.review_text.replace("\n", " ")
            self.assertTrue(self.browser.is_text_present(expected_text))

    def test_can_add_item_to_cart(self):
        self.browser.visit(self.product_page)
        self.browser.find_by_css('button[type="submit"]').click()

        # redirected to cart page
        self.assertTrue(browser.url.endswith("/cart"))

        # check for success message
        self.assertTrue(
            browser.is_text_present(
                f'Item "{self.product.name}" has been added to your cart', wait_time=2
            )
        )

        price_text = "$ {0:,.2f}".format(self.product.sale_price)

        # once for the per-unit price, and item subtotal
        self.assertEqual(browser.html.count(price_text), 2)

    def test_can_add_more_than_one_item_to_cart(self):
        helpers.clean_cart()
        self.browser.visit(self.product_page)
        self.browser.fill("quantity", self.product.on_hand)
        self.browser.find_by_css('button[type="submit"]').click()

        # redirected to cart page
        self.assertTrue(self.browser.url.endswith("/cart"))

        # check for success message
        self.assertTrue(
            self.browser.find_by_css('.alert[role="alert"]').text.endswith(
                "has been added to your cart"
            )
        )

        cart_item = self.browser.find_by_css(".cart-item").first
        per_unit_price_text = "$ {0:,.2f}".format(self.product.sale_price)
        self.assertIn(per_unit_price_text, cart_item.text)

        item_subtotal = "$ {0:,.2f}".format(
            self.product.sale_price * self.product.on_hand
        )
        self.assertIn(item_subtotal, cart_item.text)

    def test_gets_error_when_adding_too_many_to_cart(self):
        browser.visit(self.product_page)
        browser.fill("quantity", self.product.on_hand + 1)
        browser.find_by_css('button[type="submit"]').click()

        # redirected to item page
        self.assertTrue(browser.url.endswith(f"/item/{self.product.slug}"))

        # check for on-hand error message
        self.assertIn(
            f"We only have {self.product.on_hand} in stock",
            browser.find_by_css('.alert[role="alert"]').text,
        )


class StorePageTests(BaseTestClass):
    def setUp(self):
        super().setUp()
        self.page = "http://127.0.0.1:5000/store"

    def test_page_shows_available_products(self):
        """We should see a link to each item's product page."""
        self.browser.visit(self.page)
        html = browser.html

        for product in self.products:
            self.assertIn(f"/item/{product.slug}", html)

    def test_displays_NoProducts_message_if_none_available(self):
        """If no active products ahve been found, we should see a message telling us."""

        def update_products(timestamp: datetime | None):
            for product in self.products:
                product.deleted = timestamp
            Product.bulk_update(self.products, ["deleted"])

        update_products(datetime.now())
        try:
            self.browser.visit(self.page)

            # "No items" message
            self.assertTrue(browser.is_text_present("There are no items to display"))
            # no links to any item pages
            self.assertNotIn("/item/", browser.html)
        finally:
            update_products(None)

    def test_user_can_add_product_to_cart_from_page(self):
        """We should be able to add an item to our cart from the product list page."""
        self.browser.visit(self.page)

        # select first product on the page
        card_body = self.browser.find_by_css(".card-body").first
        product_name = card_body.find_by_tag("span")[0].text
        price = card_body.find_by_tag("span")[1].text

        card_body.find_by_css('button[type="submit"]').click()

        # should have been redirected to cart page
        self.assertTrue(self.browser.url.endswith("/cart"))

        self.assertTrue(
            self.browser.is_text_present(
                f'Item "{product_name}" has been added to your cart'
            )
        )

        # check that we're displaying the name of the product and price added to cart
        self.assertTrue(self.browser.is_text_present(product_name))
        self.assertTrue(self.browser.is_text_present(price))


if __name__ == "__main__":
    unittest.main()
