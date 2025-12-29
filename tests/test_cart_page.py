import pytest

from store.data import CartItem

PAGE = "http://127.0.0.1:5000/cart"


@pytest.fixture
def load_cart(cart_id, products):
    """Add two different items to the test browser's cart instance then yield to the test function."""
    for i, product in enumerate(products[:2], start=1):
        CartItem.get_or_create(cart_id=cart_id, product_id=product.id, quantity=1 * i)
    yield


def test_empty_cart(browser):
    browser.visit(PAGE)
    assert browser.is_text_present("Looks like your cart is empty.")


def test_nonempty_cart(browser, load_cart, products):
    pytest.fail("Implement test")


def test_deleting_from_cart(browser, load_cart):
    pytest.fail("Implement test")
