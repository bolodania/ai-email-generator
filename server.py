import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from cfenv import AppEnv
from sap import xssec
import functools
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.gen_ai_hub_proxy import GenAIHubProxyClient
from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from langchain.schema import HumanMessage
import re

load_dotenv()

local_testing = False

with open(os.path.join(os.getcwd(), 'env_config.json')) as f:
    aicore_config = json.load(f)

# Init the OpenAI embedding model
ai_core_client = AICoreV2Client(base_url=aicore_config['AICORE_BASE_URL'],
                            auth_url=aicore_config['AICORE_AUTH_URL'],
                            client_id=aicore_config['AICORE_CLIENT_ID'],
                            client_secret=aicore_config['AICORE_CLIENT_SECRET'],
                            resource_group=aicore_config['AICORE_RESOURCE_GROUP'])
    
        
proxy_client = GenAIHubProxyClient(ai_core_client = ai_core_client)
llm = ChatOpenAI(proxy_model_name='gpt-4o', proxy_client=proxy_client)

app = Flask(__name__)
env = AppEnv()

def generate_email_with_llm(new_payload, old_payload):
    try:
        # Extract language code from new_payload (default to EN if missing or blank)
        lang_code = (
            new_payload.get("BusinessPartnerDetails", {})
                        .get("BusinessPartnerDetails", {})
                        .get("correspondence_language", "")
                        .strip()
                        .upper()
        )
        language_name = language_code_to_name(lang_code if lang_code else "EN")

                # Determine if this is a CREATE (no old_payload or empty object)
        is_create = not old_payload or not old_payload.get("BusinessPartnerDetails")

        if is_create:
            prompt = f"""
                You are a multilingual assistant. Your task is to generate a warm, professional welcome email for a newly created Business Partner profile.

                Write the email in the language: **{language_name}**

                Here is the NEW Business Partner profile:
                {json.dumps(new_payload, indent=2)}

                Instructions:
                - Welcome the Business Partner.
                - Address the Business Partner by full name if available.
                - Mention that their profile has been successfully created.
                - Include a friendly closing.
                - Keep it concise and clear.
                - Don't generate the subject, only the email body.
                - Generate this email on behalf of "BTP Adoption & Consumption Center"
                - Format it as an HTML email body (NO code blocks like ```html).
            """
        else:
            prompt = f"""
                You are a multilingual assistant. Your task is to compare the old and new payloads of a Business Partner profile and generate a personalized, polite, and human-sounding email to inform the Business Partner about the changes made to their profile.

                Write the email in the language: **{language_name}**

                If no changes are found, reply "NO_CHANGES"

                Here is the OLD profile payload:
                {json.dumps(old_payload, indent=2)}

                Here is the NEW profile payload:
                {json.dumps(new_payload, indent=2)}

                Instructions:
                - Detect all changes.
                - Summarize them clearly.
                - Address the Business Partner by full name if available.
                - Include a friendly closing.
                - Keep it concise and clear.
                - Don't generate the subject, only the email body.
                - Generate this email on behalf of "BTP Adoption & Consumption Center"
                - Format it as an HTML (NO code blocks like ```html):.
                - Ignore change_time change_date changes.
            """
        response = llm.invoke([HumanMessage(content=prompt)])
        response_text = response.content.strip()

        # Remove code block markers if present
        return re.sub(r"^```(?:json|html)?\s*|\s*```$", "", response_text, flags=re.IGNORECASE).strip()


    except Exception as e:
        return f"Error generating email: {str(e)}"

def language_code_to_name(code):
    language_map = {
        "EN": "English",
        "DE": "German",
        "FR": "French",
        "ES": "Spanish",
        "IT": "Italian",
        "PT": "Portuguese",
        "RU": "Russian",
        "ZH": "Chinese",
        "JA": "Japanese",
        "KO": "Korean",
        "DA": "Danish",
        "FI": "Finnish",
        "SV": "Swedish",
        "NO": "Norwegian"
    }

    return language_map.get(code, "English")

port = int(os.environ.get('PORT', 3000))
if not local_testing:
    uaa_service = env.get_service(name='email-generator-uaa').credentials

# Authorization Decorator
def require_auth(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not local_testing:
            if 'authorization' not in request.headers:
                return jsonify({"error": "You are not authorized to access this resource"}), 403
            
            access_token = request.headers.get('authorization')[7:]
            security_context = xssec.create_security_context(access_token, uaa_service)
            is_authorized = security_context.check_scope('uaa.resource')

            if not is_authorized:
                return jsonify({"error": "You are not authorized to access this resource"}), 403

        return f(*args, **kwargs)  # Call the original function if authorized

    return decorated_function

@app.route("/generateEmail", methods=["POST"])
@require_auth
def generate_email():
    try:
        data = request.get_json()
        if not data or "new_payload" not in data or "old_payload" not in data:
            return jsonify({"error": "Missing 'new_payload' or 'old_payload' in request"}), 400

        new_payload = data["new_payload"]
        old_payload = data["old_payload"]
        email_text = generate_email_with_llm(new_payload, old_payload)

        return jsonify({"email_body": email_text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)

