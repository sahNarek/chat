from flask import Blueprint, request, jsonify
from core.config import app_config
from core.auth_utils import authenticate_user
from data_models.conversation import Conversation
from language_models.llm import LlmModel
from functools import wraps

completions_bp = Blueprint("completions", __name__, url_prefix="/v1")
llm_model = LlmModel(app_config.MODEL_NAME)
conversation = Conversation()
PREMIUM_ROLE = "PREMIUM_USER"


def access_level_required(access_level):
    """
    Decorator to check the access level
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_data = kwargs.get("user_data")
            if PREMIUM_ROLE in user_data.get("authorities") and app_config.TYPE == access_level:
                return func(*args, **kwargs)
            return jsonify({"error": f"This endpoint is only available for {access_level} users"}), 403
        return wrapper
    return decorator


def auth_required(func):
    """
    Decorator to check the authentication
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_data = authenticate_user(request.headers.get("Authorization").replace("Bearer ", ""))
        if not user_data:
            return jsonify({"error": "User not found"}), 404
        kwargs["user_data"] = user_data
        return func(*args, **kwargs)
    return wrapper


def handle_prompt(user_data: dict, user_prompt):
    """
    Handle the user prompt
    """
    try:
        if not user_prompt:
            return jsonify({"error": "No prompt provided"}), 400
        previous_conversations = conversation.get_user_conversations(user_data.get("sub"))
        llm_response = llm_model.generate(user_prompt, previous_conversations)
        conversation.save_conversation(user_data.get("sub"),
            {
                "role": "user",
                "content": user_prompt
            }
        )
        conversation.save_conversation(user_data.get("sub"),
            {
                "role": "assistant",
                "content": llm_response
            }
        )

        return jsonify({"response": llm_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@completions_bp.route("/premium-completions", methods=["POST"])
@auth_required
@access_level_required("premium")
def completions_premium(user_data):
    """_summary_

    Returns:
        _type_: _description_
    """
    return handle_prompt(user_data, request.json.get("prompt"))


@completions_bp.route("/completions", methods=["POST"])
@auth_required
def completions(user_data: dict):
    """
    Get completions for the given text

    Returns:
        JSON: Completions for the given text
    """
    return handle_prompt(user_data, request.json.get("prompt"))
