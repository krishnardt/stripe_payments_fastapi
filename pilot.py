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
# This is your real test secret API key.
stripe.api_key = 'sk_test_51IivqbSBdee0C8UKzcXj0dNzHxaWKvHUteGLWGeU9iRonKmJVutFUQf4WMqGZhQ975IoAuWWQBHlhhwWRGpzuCIQ002MdbejaW'



app = FastAPI(
    title='workpeer',
    description='workpeer API',
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




#! /usr/bin/env python3.6

"""
server.py
Stripe Sample.
Python 3.6 or newer required.
"""
import os
#from flask import Flask, jsonify, request



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


@app.get('/success')
def get_checout_page(request: Request):
	return templates.TemplateResponse("success.html", {"request": request})


@app.get('/cancel')
def get_checout_page(request: Request):
	return templates.TemplateResponse("cancel.html", {"request": request})

if __name__ == '__main__':
    uvicorn.run(app='pilot:app', host='127.0.0.1', port=8000, reload=True)


