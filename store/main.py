import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from pydantic import BaseModel
from redis_om import get_redis_connection, HashModel
import requests
from enviroments.config import Settings, get_settings

dotenv: Settings = get_settings()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host=dotenv.HOST,
    port=dotenv.PORT,
    password=dotenv.PASSWORD,
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
def create_order(product_order: ProductOrderCreate, background_tasks: BackgroundTasks):
    req = requests.get(
        f'http://localhost:8000/product/{product_order.product_id}')
    product = req.json()
    fee = product['price'] * 0.2
    order = Order(
        product_id=product_order.product_id,
        price=product['price'],
        fee=fee,
        total=product['price'] + fee,
        quantity=product_order.quantity,
        status='pending...'
    )
    order.save()

    background_tasks.add_task(order_complete, order)

    return order


@app.get('/order')
def get_all():
    return [format_order(pk) for pk in Order.all_pks()]


@app.get('/order/{pk}')
def get_one(pk: str):
    return format_order(pk)


def format_order(pk: str):
    return Order.get(pk)


def order_complete(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    redis.xadd(name='order-completed', fields=order.model_dump())
