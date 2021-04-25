import datetime,re,os
from datetime import date
from fastapi import Form, File,UploadFile
from typing import Optional, List, Dict#, Boolean
from pydantic import BaseModel, EmailStr, ValidationError, validator
from starlette.requests import Request







class ProductDetails(BaseModel):
	name: str
	shippable_yn: str = False
	url: str


class CreatePrice(BaseModel):
	currency: str
	amount : int
	recurring: Optional[Dict] = None

class CreateCustomer(BaseModel):
	name: str = None
	email: str = None
	phone: str = None
	payment_method: str = None
	coupon: str = None
	default_method: str = False


class CreateSubscription(BaseModel):
	""""""
	email: str
	price_id: str
