from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods= ['*'],
    allow_headers= ['*']
)

redis = get_redis_connection(
    host='redis-12878.c300.eu-central-1-1.ec2.cloud.redislabs.com',
    port='12878',
    password='0TOCYuEuly0piSZWRZn8aTIoOSLKVlWH',
    decode_responses= True
)

class Product(HashModel):
    name:str
    price: float
    quantity: int
    class Meta:
        database= redis


@app.get('/product')
async def create(product: Product):
    product.save()
    return 'Saved'