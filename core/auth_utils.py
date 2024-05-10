import jwt
from base64 import b64decode
from core.config import app_config
import logging

def authenticate_user(token):
    """_summary_

    Args:
        token (_type_): _description_

    Returns:
        _type_: _description_
    """
    secret = app_config.JWT_SECRET_KEY
    decoded_secret = b64decode(secret)

    try:
        decoded_token = jwt.decode(token, decoded_secret, algorithms=["HS256"])
        return decoded_token
        
    except jwt.DecodeError as je:
        logging.error(f"Error decoding token: {je}")
        return {"error": "Invalid token"}