from decimal import Decimal
import math

import flask
from markupsafe import Markup


star = '<i class="icon-star"></i>'
half_star = '<i class="icon-star-half-empty"></i>'
empty_star = '<i class="icon-star-empty"></i>'


def rating_stars_def(app: flask.Flask):
    @app.template_filter("rating_stars")
    def rating_stars(value: Decimal) -> str:
        result = [empty_star, empty_star, empty_star, empty_star, empty_star]
        for i in range(math.floor(value)):
            result[i] = star

        if value % 1 != 0:
            result[math.floor(value)] = half_star

        return Markup("".join(result))

    return rating_stars


def register_custom_filters(app: flask.Flask):
    rating_stars_def(app)
