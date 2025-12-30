from datetime import datetime as dt

import pytest

from store.data import Product


PAGE = "http://127.0.0.1:5000"


@pytest.fixture
def temp_delete(products):
    for p in products:
        p.deleted = dt.now()
    Product.bulk_update(products, fields=["deleted"])
    yield
    for p in products:
        p.deleted = None
    Product.bulk_update(products, fields=["deleted"])


def test_page_shows_available_products(browser, products):
    browser.visit(PAGE)
    html = browser.html

    for product in products:
        # verify we have a link to the product info page
        assert f"/item/{product.slug}" in html


def test_displays_NoProducts_message_if_none_available(browser, temp_delete):
    browser.visit(PAGE)

    # "No items" message
    assert browser.is_text_present("There are no items to display")
    # no links to any item pages
    assert "/item/" not in browser.html


def test_user_can_add_product_to_cart_from_page(browser, products, clean_cart):
    browser.visit(PAGE)

    # select first product on the page
    card_body = browser.find_by_css(".card-body").first
    product_name = card_body.find_by_tag("span")[0].text
    price = card_body.find_by_tag("span")[1].text

    card_body.find_by_css('button[type="submit"]').click()

    # should have been redirected to cart page
    assert browser.url.endswith("/cart")

    assert browser.is_text_present(f'Item "{product_name}" has been added to your cart')

    # check that we're displaying the name of the product and price added to cart
    assert browser.is_text_present(product_name)
    assert browser.is_text_present(price)
