from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Optional

app = FastAPI()

class Product(BaseModel):
    name: str
    price: float
    discount_code: Optional[str] = None

    @validator('discount_code')
    def validate_discount_code(cls, value):
        if value is None:
            return value
        if not value.startswith('DISCOUNT-'):
            # Raise a ValueError with a custom message
            raise ValueError('Discount code must start with "DISCOUNT-"')
        if len(value) < 10:
            # Raise a ValueError with another custom message
            raise ValueError('Discount code is too short. Minimum length is 10 characters.')
        return value

@app.post('/products/')
def create_product(product: Product):
    return {"message": "Product created successfully", "product_data": None}

# Hands-on Component 3: Refine Error Messages for Clarity

# Let's test the Product model with invalid discount codes.

# Step 1: Add the Product model and endpoint to your main.py file.

# Ensure your main.py now includes the Product model and the create_product endpoint as shown above.

# Step 2: Run the FastAPI application (if not already running):

# uvicorn main:app --reload
# Step 3: Send requests with invalid discount codes.

# Scenario A: Discount code does not start with "DISCOUNT-"

# Send a POST request to http://127.0.0.1:8000/products/ with:

# {
#   "name": "Super Widget",
#   "price": 99.99,
#   "discount_code": "SAVE10"
# }
# Expected Response (Status Code: 422 Unprocessable Entity):

# {
#   "detail": [
#     {
#       "loc": [
#         "body",
#         "discount_code"
#       ],
#       "msg": "Discount code must start with "DISCOUNT-"",
#       "type": "value_error"
#     }
#   ]
# }
# Observation: The custom message we defined in the ValueError is now displayed.

# Scenario B: Discount code is too short

# Send a POST request to http://127.0.0.1:8000/products/ with:

# {
#   "name": "Mega Gadget",
#   "price": 199.99,
#   "discount_code": "DISCOUNT-ABC"
# }
# Expected Response (Status Code: 422 Unprocessable Entity):

# {
#   "detail": [
#     {
#       "loc": [
#         "body",
#         "discount_code"
#       ],
#       "msg": "Discount code is too short. Minimum length is 10 characters.",
#       "type": "value_error"
#     }
#   ]
# }
# Observation: Again, our custom message is used, providing clear feedback to the user.

# 3. Global Exception Handlers: The Ultimate Customization Powerhouse

# While custom validators are excellent for field-specific logic, they do not cover all error scenarios (e.g., errors during request parsing before Pydantic validation, or other types of exceptions). For comprehensive and consistent error handling across your entire FastAPI application, global exception handlers are the most powerful tool. We will explore these in detail in the next section.

# By using custom validators, you gain fine-grained control over error messages for specific fields, significantly improving the clarity and usability of your API's error responses.