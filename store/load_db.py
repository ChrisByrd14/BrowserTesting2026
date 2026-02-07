from os.path import abspath, dirname, join, exists
from random import choice
import sys
import time

from faker import Faker
import requests

try:
    from data import db, Product, Review, Cart
except ImportError:
    from store.data import db, Product, Review, Cart


fake = Faker()

image_dir = abspath(join(dirname(__file__), 'static', 'images'))


def download_image(filename: str, product_name: str, height: int, width: int):
    resp = requests.get(f'https://via.assets.so/img.jpg?w={width}&h={height}&bg=e5e7eb&text={product_name}&fontSize=12&f=png', stream=True)
    resp.raise_for_status()

    with open(filename, 'wb') as file:
        for chunk in resp:
            file.write(chunk)
            time.sleep(0.2)
    time.sleep(0.25)


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

    # download "product images"
    for w, h in ((75, 90), (150, 150)):
        image = join(image_dir, f'{p.slug}.png')
        if h == 150:
            image = image.replace('.png', '_detail.png')
        download_image(image, p.name, h, w)

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
    # if not exists(image_dir):
    #     print(f'Image directory "{image_dir}" does not exist. Exiting.')
    #     sys.exit(0)
    # Cart.delete().execute()
    # on_hand_range = list(range(1000))
    # price_range = list(range(50, 59999, 1))  # pennies
    # with db.atomic():
    #     for _ in range(50):
    #         create_product()
    #     db.commit()

    for product in Product.select():
        img = join(image_dir, f'{product.slug}.png')
        if not exists(img):
            download_image(img, product.name, 90, 75)

        img = join(image_dir, f'{product.slug}_detail.png')
        if not exists(img):
            download_image(img, product.name, 150, 150)
