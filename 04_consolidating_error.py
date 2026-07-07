# In this practical section, we will consolidate our learning by refining the error handling in our FastAPI application. We'll focus on making the error messages even more user-friendly and ensuring our global exception handler is robust.

# Objective: To create a more polished and informative error response structure that leverages both Pydantic's validation capabilities and our custom global exception handler.

# Scenario: Imagine we are building an API for managing user profiles. We need to ensure that user data is validated correctly, and any errors are communicated clearly to the client.

# Step 1: Set up the Project and Initial Code

# Ensure you have a FastAPI project set up. If you've been following along, you can continue with the main.py file from the previous sections. If not, create a new project directory and a main.py file with the following basic structure:

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, ValidationError
from typing import List, Optional

app = FastAPI()

# --- Pydantic Models  ---

class UserProfile(BaseModel):
    user_id: int = Field(..., gt=0)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    bio: Optional[str] = Field(None, max_length=200)
    is_active: bool = True

# --- Custom Exception Handler for ValidationError ---

@app.exception_handler(ValidationError)
def validation_exception_handler(request: Request, exc: ValidationError):
    error_details = []
    for error in exc.errors():
        field_location = " ".join(map(str, error['loc']))
        message = f"Error in field '{field_location}': {error['msg']}"
        
        # Refined mapping for common Pydantic errors
        if error['type'] == 'value_error.number.gt':
            message = f"Field '{field_location}' must be a positive number."
        elif error['type'] == 'value_error.any_str.min_length':
            message = f"Field '{field_location}' is too short. Minimum length is {error['ctx']['limit_value']} characters."
        elif error['type'] == 'value_error.any_str.max_length':
            message = f"Field '{field_location}' is too long. Maximum length is {error['ctx']['limit_value']} characters."
        elif error['type'] == 'value_error.missing':
            message = f"Field '{field_location}' is required."
        elif error['type'] == 'value_error.email':
            message = f"Field '{field_location}' must be a valid email address (e.g., user@example.com)."
        elif error['type'] == 'type_error.bool':
             message = f"Field '{field_location}' must be a boolean value (true or false)."
        elif error['type'] == 'value_error': # Catch-all for custom ValueErrors
            message = f"Validation error in field '{field_location}': {error['msg']}"
            
        error_details.append({
            "field": field_location,
            "message": message,
            "code": error['type'] # Include Pydantic's error type for programmatic handling
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": error_details,
            "message": "Input validation failed. Please review the details below."
        },
    )

# --- FastAPI Endpoints ---

@app.post('/profiles/')
def create_user_profile(profile: UserProfile):
    # In a real app, you'd save this to a database
    return {"message": "User profile created successfully", "profile_data": profile.model_dump()}

@app.get('/profiles/{user_id}')
def get_user_profile(user_id: int):
    # Placeholder for fetching a profile
    return {"message": f"Profile for user {user_id} retrieved.", "user_id": user_id}
