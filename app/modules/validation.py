
def check_cart(cache: list):
    if len(cache) == 0:
        response = f'Your cart is empty'
        return response
    else:
        return{"Cart":cache}