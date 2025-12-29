from peewee import JOIN
import pytest
from selenium.webdriver.firefox.service import Service
from splinter import Browser

from store.data import db, Cart, CartItem, Product, Review
from store.load_db import create_product


_browser = None
_products = None


@pytest.fixture(scope="package")
def browser(request):
    """Create a single browser instance and injects it into tests that have "browser" as one of their arguments."""
    global _browser

    if _browser is None:
        _browser = Browser("firefox", service=Service())

    def close_browser():
        global _browser
        if _browser:
            _browser.quit()

    request.addfinalizer(close_browser)

    yield _browser


@pytest.fixture(scope="session")
def products():
    global _products

    if _products is None:
        if not len(Product.select()):
            with db.atomic():
                for _ in range(10):
                    create_product()
                db.commit()
        _products = (
            Product.select()
            .where(Product.deleted >> None)
            .join(Review, JOIN.LEFT_OUTER)
        )

    yield _products


@pytest.fixture
def clean_cart():
    """Fixture used to remove existing cart items from the database."""
    with db.atomic():
        CartItem.delete().execute()
        db.commit()
    yield


@pytest.fixture
def cart_id():
    """Get most recent Cart ID, since test browser should always be the most recent."""
    cart = Cart.select().order_by(-Cart.id).first()
    return cart.id
