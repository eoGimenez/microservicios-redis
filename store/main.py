from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host='redis-12878.c300.eu-central-1-1.ec2.cloud.redislabs.com',
    port=12878,
    password='0TOCYuEuly0piSZWRZn8aTIoOSLKVlWH',
    decode_responses=True
)


class ProductOrder(HashModel):
    product_id: str
    quantity: int

    class Meta:
        database = redis


class ProductOrderCreate(BaseModel):
    product_id: str
    quantity: int

    class Config:
        from_attributes: True


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str

    class Meta:
        database = redis


class OrderCreate(BaseModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str

    class Config:
        from_attributes: True


@app.post('/order')
def create_order(productOrder: ProductOrderCreate):
    req = requests.get(
        f'http://localhost:8000/product/{productOrder.product_id}')
    product = req.json()
    fee = product['price'] * 0.2
    order = Order(
        product_id=productOrder.product_id,
        price=product['price'],
        fee=fee,
        total=product['price'] + fee,
        quantity=productOrder.quantity,
        status='pending...'
    )
    return order.save()


@app.get('/order')
def get_all():
    return [format_order(pk) for pk in Order.all_pks()]


@app.get('/order/{pk}')
def get_one(pk: str):
    return format_order(pk)


def format_order(pk: str):
    return Order.get(pk)
