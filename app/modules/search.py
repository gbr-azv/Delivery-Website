
def find_id(id: int, cache: dict):
    for ID, Description in cache.items():
        if ID == id:
            return {"Order": Description}
    response = f'Order Not Found'
    return response