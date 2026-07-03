from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

app = FastAPI()

# --- Pydantic Models ---

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0, description="Must be greater than zero")
    tax: Optional[float] = Field(None, ge=0, le=100, description="Tax rate between 0 and 100")

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    age: int = Field(..., gt=0, lt=120)
    tags: List[str] = []

# --- FastAPI Endpoints ---

@app.post('/items/')
def create_item(item: Item):
    return {"message": "Item created successfully", "item_data": None}

@app.put('/users/{user_id}')
def update_user(user_id: int, user: User):
    return {"message": f"User {user_id} updated successfully", "user_data": None}

@app.get('/items/{item_id}')
def read_item(item_id: int):
    return {"item_id": None}


# Run the FastAPI Application

# Open your terminal in the validation_demo directory and run:

# uvicorn main:app --reload
# This will start the server, typically at http://127.0.0.1:8000.

# Step 4: Send Invalid Requests using a Tool like cURL or Postman/Insomnia

# Scenario A: Invalid Price for Item

# Send a POST request to http://127.0.0.1:8000/items/ with the following JSON body:

# {
#   "name": "Example Gadget",
#   "price": -5.00 
# }
# Expected Response (Status Code: 422 Unprocessable Entity):

# {
#   "detail": [
#     {
#       "loc": [
#         "body",
#         "price"
#       ],
#       "msg": "ensure this value is greater than 0",
#       "type": "value_error.number.gt",
#       "ctx": {
#         "limit_value": 0
#       }
#     }
#   ]
# }
# Observation: The response correctly identifies the price field in the body as the source of the error and explains that it must be greater than 0.

# Scenario B: Invalid Age and Missing Email for User

# Send a PUT request to http://127.0.0.1:8000/users/123 with the following JSON body:

# {
#   "username": "ab",
#   "age": 150
# }
# Expected Response (Status Code: 422 Unprocessable Entity):

# {
#   "detail": [
#     {
#       "loc": [
#         "body",
#         "username"
#       ],
#       "msg": "ensure this value has at least 3 characters",
#       "type": "value_error.any_str.min_length",
#       "ctx": {
#         "limit_value": 3
#       }
#     },
#     {
#       "loc": [
#         "body",
#         "email"
#       ],
#       "msg": "field required",
#       "type": "value_error.missing"
#     },
#     {
#       "loc": [
#         "body",
#         "age"
#       ],
#       "msg": "ensure this value is less than 120",
#       "type": "value_error.number.lt",
#       "ctx": {
#         "limit_value": 120
#       }
#     }
#   ]
# }
# Observation: This response is particularly insightful. It lists all the validation errors found in a single request: the username is too short, the email is missing (a required field), and the age is too high. This demonstrates FastAPI/Pydantic's ability to collect multiple errors and report them simultaneously, providing comprehensive feedback to the client.

# Scenario C: Invalid Email Format

# Send a PUT request to http://127.0.0.1:8000/users/456 with the following JSON body:

# {
#   "username": "testuser",
#   "email": "invalid-email",
#   "age": 30
# }
# Expected Response (Status Code: 422 Unprocessable Entity):

# {
#   "detail": [
#     {
#       "loc": [
#         "body",
#         "email"
#       ],
#       "msg": "value is not a valid email address",
#       "type": "value_error.email"
#     }
#   ]
# }
# Observation: The EmailStr type correctly identified the malformed email address.

# By performing these exercises, you've seen firsthand how Pydantic's validation rules translate into specific error messages and how FastAPI presents them. This understanding is crucial for the next steps, where we'll learn to refine these messages and handle errors more proactively.