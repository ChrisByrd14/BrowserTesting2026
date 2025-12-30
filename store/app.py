import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from flask import Flask, redirect, render_template, session, flash, request

from store.data import *
from store.template_filters import register_custom_filters


secret_key_file = Path("./key.py")
if not secret_key_file.exists():
    with secret_key_file.open("wt") as file:
        file.write(f"SECRET_KEY='{uuid4()}'\n")

import key

app = Flask(__name__)
app.secret_key = key.SECRET_KEY
register_custom_filters(app)


def get_or_create_cart() -> Cart:
    if session.get("session_id", None) is None:
        session["session_id"] = str(uuid4())
    return Cart.get_or_create(session_id=session["session_id"])[0]


def common_view_data() -> dict[str, Any]:
    return {
        "cart_count": len(get_cart_items(session.get("session_id", None))),
    }


@app.route("/")
@app.route("/store")
def index():
    """Store page listing all items.

    Uses JavaScript to render product cards to the page.
    """
    get_or_create_cart()

    items = [p.to_dict() for p in Product.select().where(Product.deleted >> None)]
    for item in items:
        item["sale_price"] = "{0:,.2f}".format(item["sale_price"])

    print([i["sale_price"] for i in items[:10]])
    return render_template(
        "index.html", items=json.dumps(items, default=str), **common_view_data()
    )


@app.route("/item/<slug>")
def item(slug: str):
    """Item details page.

    Does not use JavaScript.
    """
    try:
        product = Product.get(Product.slug == slug)
        if not product or product.deleted is not None:
            raise Exception()
        return render_template("item-details.html", item=product, **common_view_data())
    except:
        flash("Invalid product selected", "error")
        return redirect("/store")


@app.route("/cart")
def cart():
    try:
        cart = get_or_create_cart()
        cart_items = [
            c.to_dict()
            for c in CartItem.select().where(CartItem.cart == cart).prefetch(Product)
        ]
        return render_template("cart.html", cart_items=cart_items)
    except:
        try:
            del session["session_id"]
        except:
            ...
        flash("An error occurred.", "error")
        return redirect("/store")


@app.route("/cart/add/<slug>", methods=["POST"])
def add_item_to_cart(slug: str):
    cart = get_or_create_cart()

    product = Product.select().where(Product.slug == slug).first()
    if not product:
        raise NotImplementedError()

    qty = int(request.form.get("quantity", "0"))
    if qty > product.on_hand:
        flash(f"We only have {product.on_hand} in stock", "error")
        return redirect(f"/item/{slug}")
    elif qty < 1:
        flash("You must provide a quantity greater than 0", "error")
        return redirect(f"/item/{slug}")

    try:
        item = CartItem.get_or_create(
            cart_id=cart.id,
            product_id=product.id,
            defaults={"quantity": 0},
        )[0]

        item.quantity += qty
        item.save()
        flash(f'Item "{product.name}" has been added to your cart', "success")
        return redirect("/cart")
    except Exception as e:
        flash(f"An unexpected error occurred: {e}", "error")
        return redirect(f"/item/{slug}")


@app.route("/cart/remove/<slug>", methods=["POST"])
def remove_item_from_cart(slug: str):
    try:
        product = Product.get(slug=slug)
        cart = get_or_create_cart()
        CartItem.delete().where(
            CartItem.product == product, CartItem.cart == cart
        ).execute()
        flash(f'Item "{product.name}" has been removed from your cart')
    except Exception as e:
        print("!" * 15, f"Exception: {e}")

    return redirect("/cart")


if __name__ == "__main__":
    app.run(port=8080)
