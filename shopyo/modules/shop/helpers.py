import os
import json

from flask import session
from flask import current_app


from modules.product.models import Product

from shopyoapi.enhance import get_setting

def get_currency_symbol():
    curr_code = get_setting("CURRENCY")
    with open(
        os.path.join(
            current_app.config["BASE_DIR"],
            "modules",
            "shopman",
            "data",
            "currency.json",
        )
    ) as f:
        currencies = json.load(f)
    for curr in currencies:
        if curr["cc"] == curr_code:
            return curr["symbol"]

def get_cart_data():
    if "cart" in session:
        cart_data = session["cart"][0]
        cart_items = sum(cart_data.values())

        cart_total_price = 0
        try:
            for item in cart_data:
                print(item)
                product = Product.query.get(item)
                cart_total_price += int(cart_data[item]) * product.selling_price
        except Exception as e:
            pass

    else:
        session["cart"] = [{}]
        cart_data = session["cart"][0]
        cart_items = 0
        cart_total_price = 0

    return {
        "cart_data": cart_data,
        "cart_items": cart_items,
        "cart_total_price": cart_total_price,
    }
