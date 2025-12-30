from datetime import datetime as dt

from store.data import Product


PAGE = "http://127.0.0.1:5000/item"


def test_invalid_product_name_returns_error(browser):
    """Invalid product should redirect to store and present error"""
    browser.visit(f"{PAGE}/foo-bar-baz")

    assert browser.url == "http://127.0.0.1:5000/store"
    assert "Invalid product selected" in browser.find_by_css(".alert").text


def test_deleted_product_returns_error(browser, products):
    """Deleted product should redirect to store and present error"""
    product = products[0]
    product.deleted = dt.now()
    product.save()

    browser.visit(f"{PAGE}/{product.slug}")

    assert browser.url == "http://127.0.0.1:5000/store"
    assert "Invalid product selected" in browser.find_by_css(".alert").text
    product.deleted = None
    product.save()


def test_displays_product_data(browser, products):
    product = products[0]
    browser.visit(f"{PAGE}/{product.slug}")

    for paragraph in product.description.split("\n"):
        assert browser.is_text_present(paragraph.strip())


def test_reviews_are_displayed(browser, products):
    product = next((p for p in products if p.deleted is None and len(p.reviews) > 0))
    browser.visit(f"{PAGE}/{product.slug}")

    for i, review in enumerate(product.reviews):
        if i == 10:
            break
        expected_text = review.review_text.replace("\n", " ")
        assert browser.is_text_present(expected_text)


def test_can_add_item_to_cart(browser, products, clean_cart):
    product = products[0]
    browser.visit(f"{PAGE}/{product.slug}")
    browser.find_by_css('button[type="submit"]').click()

    # redirected to cart page
    assert browser.url.endswith("/cart")

    # check for success message
    assert browser.is_text_present(f'Item "{product.name}" has been added to your cart', wait_time=2)

    price_text = "$ {0:,.2f}".format(product.sale_price)

    # once for the per-unit price, and item subtotal
    assert browser.html.count(price_text) == 2


def test_can_add_more_than_one_item_to_cart(browser, products, clean_cart):
    product = products[0]
    browser.visit(f"{PAGE}/{product.slug}")
    browser.fill("quantity", product.on_hand)
    browser.find_by_css('button[type="submit"]').click()

    # redirected to cart page
    assert browser.url.endswith("/cart")

    # check for success message
    assert browser.find_by_css('.alert[role="alert"]').text.endswith(
        "has been added to your cart"
    )

    cart_item = browser.find_by_css(".cart-item").first
    per_unit_price_text = "$ {0:,.2f}".format(product.sale_price)
    assert per_unit_price_text in cart_item.text
    item_subtotal = "$ {0:,.2f}".format(product.sale_price * product.on_hand)
    assert item_subtotal in cart_item.text


def test_gets_error_when_adding_too_many_to_cart(browser, products, clean_cart):
    product = products[0]
    browser.visit(f"{PAGE}/{product.slug}")
    browser.fill("quantity", product.on_hand + 1)
    browser.find_by_css('button[type="submit"]').click()

    # redirected to item page
    assert browser.url.endswith(f"/item/{product.slug}")

    # check for on-hand error message
    assert (
        f"We only have {product.on_hand} in stock"
        in browser.find_by_css('.alert[role="alert"]').text
    )
