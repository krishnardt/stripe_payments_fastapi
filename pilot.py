from fastapi import FastAPI, BackgroundTasks, APIRouter, Request, Form, status, Depends, Body
from typing import List, IO, Optional
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from typing import IO
from fastapi import Header, Depends, HTTPException
from starlette import status
from pydantic import BaseModel, EmailStr
import os, uvicorn
import stripe
import schemas
import os
# This is your real test secret API key.
stripe.api_key = 'sk_test_****************************************************************'


app = FastAPI(
    title='stripe_test',
    description='stripe fastapi integration API',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc',
    )


origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )


YOUR_DOMAIN = 'http://127.0.0.1:8000'


template_dir = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
template_dir = '/home/spyder/stripe_fastapi'

# Now join the path to the actual template containing folder
template_dir = os.path.join(template_dir, "templates")
#tmplate_dir = os.path.join(template_dir, "meetings-templates")
print(template_dir)
templates = Jinja2Templates(directory=template_dir)



######################stripe functions##############################

def check_for_product(target_product = None):
    """
    returns true if product is present
    returns false if product is not present
    """
    product_list = stripe.Product.list()['data']
    product_check = False
    for product in product_list:
        if product['name'] ==target_product:
            product_check = True
            break

    return product_check


####################################################################


@app.post('/create-checkout-session')
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'inr',
                        'unit_amount': 2000,
                        'product_data': {
                            'name': 'Stubborn Attachments',
                            'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': 1,
                },
                {
                    'price_data': {
                        'currency': 'inr',
                        'unit_amount': 2000,
                        'product_data': {
                            'name': 'Stubborn Attachments',
                            'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
        )
        print("success")

        return {
            'status_code': status.HTTP_200_OK,
            'detail':checkout_session
            }
    except Exception as e:
        return {
            'status_code': status.HTTP_403_FORBIDDEN,
            'detail':str(e)
            }


@app.get('/checkout')
def get_checout_page(request: Request):
    return templates.TemplateResponse("checkout.html", {"request": request})


@app.post('/add-product')
async def add_product(product_details: schemas.ProductDetails):
    #product_details = product_details.__dict__
    product_check = check_for_product( product_details.name)
    try:
        if product_check == False:
            product = stripe.Product.create(
            name=product_details.name,
            url= product_details.url,
            shippable = product_details.shippable_yn

            )
            return JSONResponse({
                'status_code': status.HTTP_201_CREATED,
                'data': product
                })
        else:
            return JSONResponse({
                'status_code': status.HTTP_409_CONFLICT,
                'detail': 'product is already present'
                })

    except Exception as e:
        return JSONResponse({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'detail': str(e)
            })

@app.post('/products/{product_name}/add-price')
async def add_price_to_given_product(product_name: str, price_detail: schemas.CreatePrice):
    product_list = stripe.Product.list()['data']
    product_check = False
    product_id = None
    for product in product_list:
        if product_name == product['name']:
            product_check = True
            product_id = product['id']

    if product_check == False:
        return JSONResponse({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'detail': str(e)
        })
    else:
        if price_detail.recurring:
            price = stripe.Price.create(
              product=product_id,
              unit_amount=price_detail.amount,
              currency=price_detail.currency,
              recurring=price_detail.recurring,
            )
        else:
            price = stripe.Price.create(
              product=product_id,
              unit_amount=price_detail.amount,
              currency=price_detail.currency,
            )

        return JSONResponse({
            'status_code': status.HTTP_201_CREATED,
            'data': price
        })


@app.get('/product-list')
def get_product_list():
    return stripe.Product.list(limit=3);

@app.delete('/products/delete/{name}')
async def delete_product(name: str):
    product_list = stripe.Product.list()['data']

    product_det = None
    for product in product_list:
        if product['name'] == name:
            product_det = product
            break

    if product_det is None:
        return JSONResponse({
            'status_code': status.HTTP_404_NOT_FOUND,
            'detail': 'no such data'
        })
    else:
        prod_id = product_det['id']
        result = stripe.Product.delete(prod_id)
        # return JSONResponse({
        #   'status_code': status.HTTP_200_OK,
        #   'detail': product_det
        # })
        return result


@app.get('/prices-list')
async def get_prices_list():
    prices_list = stripe.Price.list()
    return prices_list


@app.get('/{product_name}/price-list')
def get_price_list_of_a_product(product_name: str):
    '''
    description: getting the price list of a given product
    first search for the product
    if you find the product, get the list of prices
    associated with it.
    '''
    product_list = stripe.Product.list()['data']
    prices_list = stripe.Price.list()['data']

    product_det = None
    for product in product_list:
        if product['name'] == product_name:
            product_det = product
            break

    if product_det is None:
        return JSONResponse({
            'status_code': status.HTTP_404_NOT_FOUND,
            'detail': 'no such product'
        })
    else:
        print(product_det)
        prod_id = product_det['id']
        print(prod_id)
        price_list = []
        for price in prices_list:
            print(price['product'], prod_id)
            if price['product'] == prod_id:
                price_list.append(price)

        return JSONResponse({
            'status_code':status.HTTP_200_OK,
            'data':price_list,
            })







@app.get('/products/{name}')
async def delete_product(name: str):
    product_list = stripe.Product.list()['data']

    product_det = None
    for product in product_list:
        if product['name'] == name:
            product_det = product
            break

    if product_det is None:
        return JSONResponse({
            'status_code': status.HTTP_404_NOT_FOUND,
            'detail': 'no such data'
        })
    else:
        return JSONResponse({
            'status_code': status.HTTP_200_OK,
            'detail': product_det
        })




#tasks
'''
1. create customer
2. retrieve customer
3. list of customers
4. create invoice
   a. search for the customer
   b. if the customer is in the list,use that one
   c. else, create new customer with the given details
   d. generate invoice
'''

@app.get('/customer-list')
def get_customer_list():
    customers_list = stripe.Customer.list()
    return customers_list


@app.post('/create-customer')
async def create_customer(customer_det: schemas.CreateCustomer):
    
    customers_list = stripe.Customer.list()
    check_customer = False
    result = None
    for customer in customers_list:
        if customer['email'] == customer_det.email:
            print("cusotmer data found")
            check_customer = True
            result = customer
            break

    print(check_customer)
    if check_customer == False:
        if customer_det.default_method == False:
            result = stripe.Customer.create(
                name = customer_det.name,
                email = customer_det.email,
                phone = customer_det.phone,
                payment_method = customer_det.payment_method,
                coupon = customer_det.coupon,
                description="My First Test Customer (created for API docs)",
            )
        else:
            result = stripe.Customer.create(
                name = customer_det.name,
                email = customer_det.email,
                phone = customer_det.phone,
                payment_method = customer_det.payment_method,
                coupon = customer_det.coupon,
                invoice_settings={
                    'default_payment_method': customer_det.payment_method,
                  },
                description="My First Test Customer (created for API docs)",
            )


    return result


@app.delete('/delete-customer/{name}')
async def deleting_customer(name: str):
    customers_list = stripe.Customer.list()
    customer_data = None
    for customer in customers_list:
        if customer['email'] == name:
            customer_data = customer
            break

    if customer_data is None:
        return JSONResponse({
            'status_code':status.HTTP_404_NOT_FOUND,
            'detail': 'no such customer'
            })
    else:
        delete_status = stripe.Customer.delete(customer_data['id'])
        print(delete_status)
        return JSONResponse({
            'status_code':status.HTTP_202_ACCEPTED,
            'detail':f'customer with email id {customer_data["email"]} is  deleted'
            })



@app.get('/product-subscriptions/{product_name}')
def get_product_subscriptions(product_name: str):

    products_list = stripe.Product.list()['data']
    product_data = None

    for product in products_list:
        if product['name'] == product_name:
            product_data = product['id']
            break

    if product_data is not None:
        prices_list = stripe.Price.list()['data']
        prices_data = {}
        for price in prices_list:
            if price['product'] == product_data:
                prices_data[price['id']] = price

        return JSONResponse({
            'status_code': status.HTTP_200_OK,
            'data':prices_data
            })

    else:
        return JSONResponse({
            'status_code':status.HTTP_404_NOT_FOUND,
            'detail': f'no product with name {product_name}'
            })



@app.post('/create-subscription')
async def creating_user_subscription(subscribe_data: schemas.CreateSubscription):
    """
    requirements:
    1. add current user here when using it in production to get the email and login checks
    prams:
    @email: email of the user who is subscribing
    @price_id: id ofthe price, this we can fetch from the click option
    if user and price list already present....
    """
    customers_list = stripe.Customer.list()['data']
    customer_id = None
    for customer in customers_list:
        if customer['email'] == subscribe_data.email:
            customer_id= customer['id']




    products_list = stripe.Product.list()['data']
    product_data = None

    # for product in products_list:
    #   if product['name'] == subscribe_data.product_name:
    #       product_data = product['id']
    #       break
    price_id = 'price_**********************************'
    #price_id = stripe.Price.retrieve(subscribe_data.price_id)

    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{
        'price': price_id,
        }],
        add_invoice_items=[{
        #'price': '{{PRICE_ID}}',
        }],
    )

    print(subscription)

    return subscription



@app.get('/success')
def get_checout_page(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})


@app.get('/cancel')
def get_checout_page(request: Request):
    return templates.TemplateResponse("cancel.html", {"request": request})

if __name__ == '__main__':
    uvicorn.run(app='pilot:app', host='127.0.0.1', port=8000, reload=True)


