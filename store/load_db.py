from random import choice

from faker import Faker

try:
    from data import db, Product, Review, Cart
except ImportError:
    from store.data import db, Product, Review, Cart


fake = Faker()


def create_product():
    on_hand_range = list(range(1000))
    price_range = list(range(50, 59999, 1))  # pennies

    name = fake.bs()
    purchase_price = choice(price_range) / 100
    p = Product.create(
        name=name,
        slug=fake.slug(name),
        description="\n".join(fake.paragraphs(choice(range(2, 4)))),
        purchase_price=f"{purchase_price:0.2f}",
        sale_price=f"{purchase_price * 1.75:0.2f}",
        on_hand=choice(on_hand_range),
    )

    if not choice((1, 1, 0)):
        # approx 1/3 of items won't have any reviews
        return

    for _ in range(choice(range(20))):
        Review.create(
            reviewer=fake.name(),
            review_text="\n".join(fake.paragraphs(choice(range(5, 25)))),
            rating=choice((0.5, 1.0, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5)),
            product_id=p.id,
        )


if __name__ == "__main__":
    Cart.delete().execute()
    on_hand_range = list(range(1000))
    price_range = list(range(50, 59999, 1))  # pennies
    with db.atomic():
        for _ in range(50):
            create_product()
        db.commit()
