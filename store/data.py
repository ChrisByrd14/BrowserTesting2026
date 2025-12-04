from datetime import datetime
import os.path

import peewee


db = peewee.SqliteDatabase(os.path.join(os.path.dirname(__file__), "..", "store.db"))


class __BaseModel(peewee.Model):
    dict_date_format = "%Y-%m-%d %H:%M:%S"

    class Meta:
        database = db

    id = peewee.PrimaryKeyField()
    created = peewee.DateTimeField(default=datetime.now)
    updated = peewee.DateTimeField(null=True)
    deleted = peewee.DateTimeField(null=True)

    def to_dict(self):
        result = {"id": self.id}
        for column in ("created", "updated", "deleted"):
            if val := getattr(self, column):
                result[column] = val.strftime(self.dict_date_format) if val else None

        return result

    def save(self, *args, **kwargs):
        if self.id:
            # this record has already been saved to the DB, so we must be updating
            self.updated = datetime.now()
        super().save(*args, **kwargs)


class Product(__BaseModel):
    name = peewee.CharField()
    slug = peewee.CharField()
    description = peewee.TextField()
    purchase_price = peewee.DecimalField(max_digits=9)
    sale_price = peewee.DecimalField(max_digits=9)
    on_hand = peewee.IntegerField()

    def to_dict(self):
        return {
            **super().to_dict(),
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            # "purchase_price": self.purchase_price,
            "sale_price": self.sale_price,
            "on_hand": self.on_hand,
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
        }


class Review(__BaseModel):
    reviewer = peewee.CharField()
    review_text = peewee.TextField()
    rating = peewee.DecimalField()
    product_id = peewee.ForeignKeyField(Product, backref="reviews")


class Cart(__BaseModel):
    session_id = peewee.CharField(unique=True)


class CartItem(__BaseModel):
    cart = peewee.ForeignKeyField(Cart, backref="items")
    product_id = peewee.ForeignKeyField(Product, backref="carts")
    quantity = peewee.IntegerField()


db.connect()
db.create_tables([Product, Review, Cart, CartItem], safe=True)


def get_cart_items(session_id: str | None, **kwargs) -> list[CartItem]:
    try:
        if not session_id:
            raise ValueError()

        return list(Cart.get(session_id=session_id).items)
    except:
        return []
