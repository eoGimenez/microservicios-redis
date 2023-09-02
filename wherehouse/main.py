from fastapi import FastAPI
from pydantic import BaseModel
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
    port=12878,
    password='0TOCYuEuly0piSZWRZn8aTIoOSLKVlWH',
    decode_responses= True
)

class Product(HashModel):
    name:str
    price: float
    quantity: int

    class Meta:
        database = redis

class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int

    class Config:
        from_attributes = True

@app.get('/product')
def all():
    return [format_products(pk) for pk in Product.all_pks()]

@app.post('/product')
def create(product: ProductCreate):
    product_instance = Product(**product.model_dump())
    return product_instance.save()


@app.get('/product/{pk}')
def get_one(pk: str):
    return Product.get(pk)

@app.delete('/product/{pk}')
def delete(pk: str):
    return Product.delete(pk)

def format_products(pk: str):
    return Product.get(pk)