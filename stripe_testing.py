import stripe


stripe.api_key = 'sk_test_51IivqbSBdee0C8UKzcXj0dNzHxaWKvHUteGLWGeU9iRonKmJVutFUQf4WMqGZhQ975IoAuWWQBHlhhwWRGpzuCIQ002MdbejaW'

response = stripe.Charge.create(
  amount=2000,
  currency="inr",
  source="tok_amex", # obtained with Stripe.js
  metadata={'order_id': '6735'}
)



print(response)




customers = stripe.Customer.list(limit=3)
print(customers)
for customer in customers.auto_paging_iter():
	print(customer)


# balance = stripe.Balance.retrieve()
# print(balance)





stripe.Customer.create(
	name='Ravi'
  description="My First Test Customer (created for API docs)",
)

