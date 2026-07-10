# What are Global Exception Handlers?

# FastAPI allows you to define custom handlers for specific exception types. When an exception of a registered type occurs anywhere in your application, FastAPI will execute your custom handler instead of its default error handling. This gives you complete control over the response format, status code, and content for various error scenarios.

# The @app.exception_handler() Decorator:

# FastAPI provides the @app.exception_handler() decorator to register custom exception handlers. This decorator takes the exception type as an argument.

# The handler function itself typically accepts two arguments:

# request: An instance of fastapi.Request, providing details about the incoming request.
# exc: The exception instance that was caught.
# The handler function must return a FastAPI Response object (e.g., a JSONResponse).

# Handling ValidationError Globally:

# The most common use case for global exception handlers in the context of Pydantic valid
ation is to override FastAPI's default handling of ValidationError. This allows you to standardize the error response format for all validation failures, even if they originate from different parts of your application or involve different Pydantic models.

# Hands-on Component 2: Implement a Custom Exception Handler for Validation Errors

# Let's modify our existing FastAPI application to include a global exception handler for ValidationError.

# Step 1: Update main.py

# We will add a new function decorated with @app.exception_handler(ValidationError). This handler will iterate through the errors reported by Pydantic and construct a more user-friendly JSON response.

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, ValidationError, field_validator
from typing import List, Optional

app = FastAPI()

# --- Pydantic Models ---

class Item(BaseModel):
    name: str = Field(..., min_length=1, description="The name of the item.")
    description: Optional[str] = Field(..., description="A brief description of the item.")
    price: float = Field(..., gt=0, description="Item price must be positive.")
    tax: Optional[float] = Field(..., ge=0, le=100, description="Tax rate must be between 0 and 100.")

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    age: int = Field(..., gt=0, lt=120)
    tags: List[str] = []

class Product(BaseModel):
    name: str
    price: float
    discount_code: Optional[str] = Field(None, alias='discountCode') # Example of alias for JSON input

    @field_validator('discount_code')
    @classmethod
    def validate_discount_code(cls, value):
        if value is None:
            return value
        if not value.startswith('DISCOUNT-'):
            raise ValueError('Discount code must start with "DISCOUNT-"')
        if len(value) < 10:
            raise ValueError('Discount code is too short. Minimum length is 10 characters.')
        return value

# --- Custom Exception Handler for ValidationError ---

@app.exception_handler(ValidationError)
def validation_exception_handler(request: Request, exc: ValidationError):
    # Build a list of user-friendly error messages
    error_messages = []
    for error in exc.errors():
        field_location = " ".join(map(str, error['loc'])) # e.g., 'body username'
        message = f"Error in field '{field_location}': {error['msg']}"
        
        # More specific message mapping based on error type (optional but recommended)
        if error['type'] == 'value_error.number.gt':
            message = f"Field '{field_location}' must be greater than {error['ctx']['limit_value']}."
        elif error['type'] == 'value_error.any_str.min_length':
            message = f"Field '{field_location}' must be at least {error['ctx']['limit_value']} characters long."
        elif error['type'] == 'value_error.missing':
            message = f"Field '{field_location}' is required."
        elif error['type'] == 'value_error.email':
            message = f"Field '{field_location}' must be a valid email address."
        elif error['type'] == 'value_error': # Catch-all for custom ValueErrors like from validators
            # For custom validators, the 'msg' is often already user-friendly
            message = f"Error in field '{field_location}': {error['msg']}"
            
        error_messages.append(message)

    # You can also structure the response differently, e.g., a list of errors
    # or a dictionary with a general error message and a details list.
    return JSONResponse(
        status_code=422, # Unprocessable Entity
        content={
            "detail": None,
            "message": "Input validation failed. Please check the provided data."
        },
    )

# --- FastAPI Endpoints ---

@app.post('/items/')
def create_item(item: Item):
    return {"message": "Item created successfully", "item_data": item.dict()}

@app.put('/users/{user_id}')
def update_user(user_id: int, user: User):
    return {"message": f"User {user_id} updated successfully", "user_data": user.dict()}

@app.post('/products/')
def create_product(product: Product):
    return {"message": "Product created successfully", "product_data": product.dict()}

@app.get('/items/{item_id}')
def read_item(item_id: int):
    return {"item_id": item_id}
