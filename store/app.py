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


def common_view_data() -> dict[str, Any]:
    return {
        "cart_count": len(get_cart_items(session.get("session_id", None))),
    }


@app.route("/")
@app.route("/store")
def index():
    if "session_id" not in session:
        session_id = str(uuid4())
        Cart.create(session_id=session_id)
        session["session_id"] = session_id

    items = [p.to_dict() for p in Product.select().where(Product.deleted >> None)]
    return render_template(
        "index.html", items=json.dumps(items, default=str), **common_view_data()
    )


@app.route("/item/<slug>")
def item(slug: str):
    product = Product.get(Product.slug == slug)
    if not product:
        raise NotImplementedError()
    return render_template("item-details.html", item=product, **common_view_data())


@app.route("/cart")
def cart():
    if "session_id" not in session:
        flash("An error occurred.", "error")
        return redirect("/store")
    cart = Cart.get(session_id=session["session_id"])
    cart_items = [
        c.to_dict()
        for c in CartItem.select().where(CartItem.cart == cart).prefetch(Product)
    ]
    return render_template("cart.html", cart_items=cart_items)


@app.route("/cart/add/<slug>", methods=["POST"])
def add_item_to_cart(slug: str):
    product = Product.get(slug=slug)
    if not product:
        raise NotImplementedError()

    item = CartItem.get_or_create(
        cart_id=Cart.get_or_create(session_id=session["session_id"])[0].id,
        product_id=product.id,
        defaults={"quantity": 0},
    )[0]

    qty = int(request.form.get("quantity", "0"))
    if qty > product.on_hand:
        flash(f"We only have {product.on_hand} in stock", "error")
        return redirect(f"/item/{slug}")
    elif qty < 1:
        flash("You must provide a quantity greater than 0", "error")
        return redirect(f"/item/{slug}")

    item.quantity += qty

    try:
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
        cart = Cart.get(session_id=session["session_id"])
        CartItem.delete().where(
            CartItem.product == product, CartItem.cart == cart
        ).execute()
        flash(f'Item "{product.name}" has been removed from your cart')
    except Exception as e:
        print("!" * 15, f"Exception: {e}")

    return redirect("/cart")


if __name__ == "__main__":
    app.run(port=8080)
