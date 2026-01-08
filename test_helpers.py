from peewee import JOIN

from store.data import *
from store.load_db import create_product


def get_products() -> list[Product]:
    """Check for products in the DB. If none exist then create some, and return them as a list"""
    if not len(Product.select()):
        with db.atomic():
            for _ in range(10):
                create_product()
            db.commit()

    return Product.select().where(Product.deleted >> None).join(Review, JOIN.LEFT_OUTER)


def clean_cart():
    with db.atomic():
        CartItem.delete().execute()
        db.commit()


def load_cart(cart_id, products):
    for i, product in enumerate(products, start=1):
        CartItem.get_or_create(cart_id=cart_id, product_id=product.id, quantity=1 * i)
