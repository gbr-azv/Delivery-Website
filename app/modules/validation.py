from fastapi import status, HTTPException

def check_cart(cache: list):
    if len(cache) == 0:
        response = f'Your cart is empty'
        return response
    else:
        return cache
    
def check_id(id: int, cache: dict):
    if id in cache:
        del cache[id]
        return{"Cart Updated":f'Your Deleted Order ID: {id}'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Order With ID {id} Not Found')
    
#def del_order(id: int, cache: dict):
#    del cache[id]

def find_id(id: int, cache: dict):
    for ID, Description in cache.items():
        if ID == id:
            return {"Order": Description}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Order With ID {id} Not Found')