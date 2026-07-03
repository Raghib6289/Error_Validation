# Practice Exercises to Reinforce Learning:

# Create a Pydantic model for a Book with fields like title (string, min length 5), author (string, min length 3), publication_year (integer, between 1000 and current year), and an optional isbn (string, must match a specific regex pattern like ^\d{10}(\d{3})?$). Implement a FastAPI endpoint to receive and validate Book objects. Send invalid data to test all constraints.
# Enhance the Book model: Add a custom validator for publication_year to ensure it is not in the future. Refine the error message for this custom validation.
# Implement a Global Exception Handler: Modify your FastAPI application to catch ValidationError and return a standardized JSON response with user-friendly messages and error codes, similar to the UserProfile example.
# Simulate a Non-Validation Error: Add a simple endpoint that intentionally raises a generic Exception (e.g., 1 / 0) and implement a global handler for Exception to return a generic "Internal Server Error" message, ensuring sensitive details are not exposed.


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

app = FastAPI(title="Book API Practice")

# ==========================================
# Exercises 1 & 2: Pydantic Model Validation
# ==========================================
class Book(BaseModel):
    title: str = Field(..., min_length=5, description="Title of the book")
    author: str = Field(..., min_length=3, description="Author of the book")
    # Base boundary for ge (greater than or equal to). Upper boundary handled in custom validator.
    publication_year: int = Field(..., ge=1000)
    # Using the pattern parameter for regex matching
    isbn: Optional[str] = Field(None, pattern=r'^\d{10}(\d{3})?$')

    @field_validator('publication_year')
    @classmethod
    def check_year_not_in_future(cls, v: int) -> int:
        current_year = datetime.now().year
        if v > current_year:
            # Refined error message specific to the custom validation
            raise ValueError(f"Publication year cannot be in the future. Received {v}, but max allowed is {current_year}.")
        return v


# ==========================================
# Exercise 3: Global Validation Handler
# ==========================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Catches Pydantic validation errors and formats them into a clean, user-friendly JSON response."""
    errors = []
    for error in exc.errors():
        # Cleanly format the location of the error (e.g., body -> title)
        field_path = " -> ".join(map(str, error.get("loc", [])))
        errors.append({
            "field": field_path,
            "issue": error.get("msg")
        })
        
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_FAILED",
            "message": "The submitted data did not pass validation checks.",
            "details": errors
        }
    )


# ==========================================
# Exercise 4: Global Generic Exception Handler
# ==========================================
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catches unhandled server errors to prevent leaking sensitive traceback details."""
    # In a real app, you would log `exc` to your monitoring system (e.g., Sentry, Datadog) here.
    print(f"CRITICAL ERROR: {exc}") 
    
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred on our end. Please try again later."
        }
    )


# ==========================================
# API Endpoints
# ==========================================
@app.post("/books/", tags=["Books"])
async def create_book(book: Book):
    """Endpoint to receive and validate Book objects."""
    return {"message": "Book accepted successfully!", "data": book}


@app.get("/simulate-error/", tags=["Testing"])
async def simulate_error():
    """Endpoint that intentionally raises a generic Exception (Division by Zero)."""
    return 1 / 0


# 1. Testing Invalid Data (Will trigger the Exercise 3 Handler)
# Send this JSON payload to POST /books/:

# JSON
# {
#   "title": "IT", 
#   "author": "SK", 
#   "publication_year": 2050, 
#   "isbn": "123" 
# }
# Expected Custom Response:

# JSON
# {
#   "error_code": "VALIDATION_FAILED",
#   "message": "The submitted data did not pass validation checks.",
#   "details": [
#     {
#       "field": "body -> title",
#       "issue": "String should have at least 5 characters"
#     },
#     {
#       "field": "body -> author",
#       "issue": "String should have at least 3 characters"
#     },
#     {
#       "field": "body -> publication_year",
#       "issue": "Value error, Publication year cannot be in the future. Received 2050, but max allowed is 2026."
#     },
#     {
#       "field": "body -> isbn",
#       "issue": "String should match pattern '^\\d{10}(\\d{3})?$'"
#     }
#   ]
# }
# 2. Testing the Non-Validation Error (Will trigger the Exercise 4 Handler)
# Simply navigate your browser or send a GET request to http://127.0.0.1:8000/simulate-error/.

# Expected Secure Response:

# JSON
# {
#   "error_code": "INTERNAL_SERVER_ERROR",
#   "message": "An unexpected error occurred on our end. Please try again later."
# }