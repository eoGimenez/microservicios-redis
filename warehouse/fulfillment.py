import time
from main import redis, Product

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
                try:
                    if (product.quantity >= obj['quantity']):
                        product = Product.get(obj['product_id'])
                        product.quantity -= int(obj['quantity'])
                        product.save()
                        print(product)
                    else:
                        redis.xadd(name = 'refund-order', fields = obj)
                except:
                    redis.xadd(name = 'refund-order', fields = obj)
    except Exception as e:
        print(str(e))
    time.sleep(3)