from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from config import SECRET_KEY, ALGORITHM
from . import models
from .database import get_db

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication failed", status_code: int = 401):
        super().__init__(status_code=status_code, detail=detail)

class ValidationError(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)

async def validate_bearer_token(token: str = Depends(oauth2_scheme)) -> dict:
    """Validate JWT bearer token and return user data"""
    try:
        # Decode the JWT token using the secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise AuthenticationError("Invalid token: missing user identifier")
        
        # Return user data from token
        return {"username": username, "token_payload": payload}
        
    except ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except JWTError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")
    except Exception as e:
        raise AuthenticationError(f"Token validation failed: {str(e)}")

def validate_shopping_list_id(shopping_list_id: int, db: Session = Depends(get_db)) -> models.ShoppingList:
    """Validate that shopping list exists and return it"""
    if shopping_list_id <= 0:
        raise ValidationError("Shopping list ID must be a positive integer")
    
    shopping_list = db.query(models.ShoppingList).filter(models.ShoppingList.id == shopping_list_id).first()
    if not shopping_list:
        raise ValidationError("Shopping list not found", status_code=404)
    
    return shopping_list

def validate_shopping_list_item_id(item_id: int, db: Session = Depends(get_db)) -> models.ShoppingListItem:
    """Validate that shopping list item exists and return it"""
    if item_id <= 0:
        raise ValidationError("Shopping list item ID must be a positive integer")
    
    item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if not item:
        raise ValidationError("Shopping list item not found", status_code=404)
    
    return item

def validate_authenticated_shopping_list_access(
    shopping_list_id: int,
    current_user: dict = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
) -> models.ShoppingList:
    """Validate token and shopping list access"""
    shopping_list = validate_shopping_list_id(shopping_list_id, db)
    return shopping_list

def validate_authenticated_shopping_list_item_access(
    item_id: int,
    current_user: dict = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
) -> models.ShoppingListItem:
    """Validate token and shopping list item access"""
    item = validate_shopping_list_item_id(item_id, db)
    return item