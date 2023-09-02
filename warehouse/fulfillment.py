import time
from main import redis, Product, ProductCreate

key = 'order-completed'
group = 'warehouse-group'

try:
    redis.xgroup_create(name=key, groupname=group, mkstream=True)
    print('Group created')
except Exception as e:
    print(str(e))

while True:
    try:
        results = redis.xreadgroup(groupname=group, consumername=key, streams={key: '>'}) 
        print(results)
        if results != []:
            for result in results:
                obj = result[1][0][1]
                product = Product.get(obj['product_id'])
                product.quantity -= int(obj['quantity'])
                product.save()
                print(product)
    except Exception as e:
        print(str(e))
    time.sleep(3)