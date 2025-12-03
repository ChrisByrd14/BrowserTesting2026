import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from flask import Flask, redirect, render_template, session

from .data import *


secret_key_file = Path("./key.py")
if not secret_key_file.exists():
    with secret_key_file.open("wt") as file:
        file.write(f"SECRET_KEY='{uuid4()}'\n")

import key

app = Flask(__name__)
app.secret_key = key.SECRET_KEY


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
    print(items)
    return render_template(
        "index.html", items=json.dumps(items, default=str), **common_view_data()
    )


@app.route("/item/<slug>")
def item(slug: str):
    product = Product.get(Product.slug == slug)
    if not product:
        raise NotImplementedError()
    return render_template("item-details.html", item=product, **common_view_data())


if __name__ == "__main__":
    app.run(port=8080)
