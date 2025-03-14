import os
import json
import requests
from flask import current_app
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_PROMPT_TEMPLATE = """
Você é um assistente espiritual baseado em ensinamentos bíblicos. Seu objetivo é fornecer
orientação, conforto e sabedoria inspirada na Bíblia. Por favor, responda à seguinte
mensagem com uma perspectiva bíblica, citando versículos relevantes quando apropriado:

MENSAGEM DO USUÁRIO: {message}
"""

# Provider-specific handlers


def openai_chat(api_key, model, message):
    """Get response from OpenAI API"""
    # Check if we're in development mode and should use mock responses
    logger.info(
        f"ENV: {current_app.config.get('ENV')}, USE_MOCK_LLM: {current_app.config.get('USE_MOCK_LLM', False)}")
    if current_app.config.get('ENV') == 'development' and current_app.config.get('USE_MOCK_LLM', False):
        logger.info("Using mock response for OpenAI in development mode")
        return f"Resposta simulada para: '{message}'\n\nComo diz em João 3:16, 'Porque Deus amou o mundo de tal maneira que deu o seu Filho unigênito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna.'"

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    prompt = DEFAULT_PROMPT_TEMPLATE.format(message=message)

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Você é um assistente espiritual que oferece orientação baseada na Bíblia."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenAI API error: {str(e)}")
        if response and response.text:
            logger.error(f"Response: {response.text}")
        raise Exception(f"Error calling OpenAI API: {str(e)}")


def anthropic_chat(api_key, model, message):
    """Get response from Anthropic Claude API"""
    # Check if we're in development mode and should use mock responses
    if current_app.config.get('ENV') == 'development' and current_app.config.get('USE_MOCK_LLM', False):
        logger.info("Using mock response for Anthropic in development mode")
        return f"Resposta simulada para: '{message}'\n\nComo diz em Salmos 23:1, 'O Senhor é o meu pastor, nada me faltará.'"

    url = "https://api.anthropic.com/v1/messages"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }

    prompt = DEFAULT_PROMPT_TEMPLATE.format(message=message)

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result["content"][0]["text"].strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"Anthropic API error: {str(e)}")
        if response and response.text:
            logger.error(f"Response: {response.text}")
        raise Exception(f"Error calling Anthropic API: {str(e)}")


def google_chat(api_key, model, message):
    """Get response from Google Gemini API"""
    # Check if we're in development mode and should use mock responses
    if current_app.config.get('ENV') == 'development' and current_app.config.get('USE_MOCK_LLM', False):
        logger.info("Using mock response for Google in development mode")
        return f"Resposta simulada para: '{message}'\n\nComo diz em Provérbios 3:5-6, 'Confia no Senhor de todo o teu coração e não te estribes no teu próprio entendimento. Reconhece-o em todos os teus caminhos, e ele endireitará as tuas veredas.'"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    prompt = DEFAULT_PROMPT_TEMPLATE.format(message=message)

    data = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 800
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"Google API error: {str(e)}")
        if response and response.text:
            logger.error(f"Response: {response.text}")
        raise Exception(f"Error calling Google API: {str(e)}")


def mistral_chat(api_key, model, message):
    """Get response from Mistral AI API"""
    # Check if we're in development mode and should use mock responses
    if current_app.config.get('ENV') == 'development' and current_app.config.get('USE_MOCK_LLM', False):
        logger.info("Using mock response for Mistral in development mode")
        return f"Resposta simulada para: '{message}'\n\nComo diz em Mateus 11:28, 'Vinde a mim, todos os que estais cansados e oprimidos, e eu vos aliviarei.'"

    url = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    prompt = DEFAULT_PROMPT_TEMPLATE.format(message=message)

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Você é um assistente espiritual que oferece orientação baseada na Bíblia."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"Mistral API error: {str(e)}")
        if response and response.text:
            logger.error(f"Response: {response.text}")
        raise Exception(f"Error calling Mistral API: {str(e)}")


def generic_chat(api_key, model, message, provider):
    """Fallback for other providers - tries to use a standard format"""
    # Check if we're in development mode and should use mock responses
    if current_app.config.get('ENV') == 'development' and current_app.config.get('USE_MOCK_LLM', False):
        logger.info(f"Using mock response for {provider} in development mode")
        return f"Resposta simulada para: '{message}'\n\nComo diz em Filipenses 4:13, 'Posso todas as coisas naquele que me fortalece.'"

    logger.warning(f"Using generic handler for provider: {provider}")

    # For demonstration, we'll use a simple approach similar to OpenAI
    url = f"https://api.{provider}.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    prompt = DEFAULT_PROMPT_TEMPLATE.format(message=message)

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Você é um assistente espiritual que oferece orientação baseada na Bíblia."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        # Try to parse the response in a format similar to OpenAI
        if "choices" in result and len(result["choices"]) > 0:
            if "message" in result["choices"][0]:
                return result["choices"][0]["message"]["content"].strip()

        # Fallback to returning the entire response as string
        return json.dumps(result)
    except requests.exceptions.RequestException as e:
        logger.error(f"{provider} API error: {str(e)}")
        if response and response.text:
            logger.error(f"Response: {response.text}")
        raise Exception(f"Error calling {provider} API: {str(e)}")


def get_llm_response(provider, model, api_key, message):
    """
    Get response from the specified LLM provider

    Args:
        provider: The LLM provider (openai, anthropic, google, etc.)
        model: The model name
        api_key: The API key for the provider
        message: The user message to process

    Returns:
        The LLM response as text
    """
    provider = provider.lower()

    # Delegate to appropriate provider handler
    if provider == 'openai':
        return openai_chat(api_key, model, message)
    elif provider == 'anthropic':
        return anthropic_chat(api_key, model, message)
    elif provider == 'google':
        return google_chat(api_key, model, message)
    elif provider == 'mistral':
        return mistral_chat(api_key, model, message)
    else:
        return generic_chat(api_key, model, message, provider)

# Definition of LLM service providers for use in the chat API


class LLMService:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_response(self, message, model=None):
        raise NotImplementedError("Subclasses must implement this method")

    def format_prompt(self, message, template=None, context=None):
        if not template:
            return message

        # Basic template formatting with context
        formatted = template.format(message=message)
        if context:
            # Add any context-specific formatting here if needed
            pass
        return formatted


class OpenAIService(LLMService):
    def get_response(self, message, model="gpt-3.5-turbo"):
        return openai_chat(self.api_key, model, message)


class AnthropicService(LLMService):
    def get_response(self, message, model="claude-3-haiku-20240307"):
        return anthropic_chat(self.api_key, model, message)


class GoogleService(LLMService):
    def get_response(self, message, model="gemini-pro"):
        return google_chat(self.api_key, model, message)


class MistralService(LLMService):
    def get_response(self, message, model="mistral-medium"):
        return mistral_chat(self.api_key, model, message)


class GenericService(LLMService):
    def __init__(self, api_key=None, provider="generic"):
        super().__init__(api_key)
        self.provider = provider

    def get_response(self, message, model=None):
        return generic_chat(self.api_key, model, message, self.provider)


# Map of provider names to service classes
LLM_SERVICES = {
    'openai': OpenAIService,
    'anthropic': AnthropicService,
    'google': GoogleService,
    'mistral': MistralService,
    'generic': GenericService
}
