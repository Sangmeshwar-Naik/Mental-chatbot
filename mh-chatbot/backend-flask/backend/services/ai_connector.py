"""
Multi-provider AI Connector Service
Supports: Google Gemini, OpenAI, Anthropic Claude, Groq
"""
import os
from typing import List, Dict, Optional, Generator
from flask import current_app


class AIConnector:
    """Universal AI provider connector"""
    
    def __init__(self):
        self.provider = current_app.config.get('AI_PROVIDER', 'gemini')
        self.model_name = current_app.config.get('AI_MODEL_NAME', 'gemini-1.5-pro')
        self.temperature = current_app.config.get('AI_TEMPERATURE', 0.7)
        self.max_tokens = current_app.config.get('AI_MAX_TOKENS', 2048)
        self.streaming = current_app.config.get('AI_STREAMING', True)
        
        # Initialize provider client
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AI provider client based on configuration"""
        if self.provider == 'gemini':
            return self._init_gemini()
        elif self.provider == 'openai':
            return self._init_openai()
        elif self.provider == 'anthropic':
            return self._init_anthropic()
        elif self.provider == 'groq':
            return self._init_groq()
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    def _init_gemini(self):
        """Initialize Google Gemini"""
        try:
            import google.generativeai as genai
            api_key = current_app.config.get('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not configured")
            genai.configure(api_key=api_key)
            # Use models/ prefix for Gemini model names
            model_name = self.model_name or 'gemini-2.5-flash'
            if not model_name.startswith('models/'):
                model_name = f'models/{model_name}'
            return genai.GenerativeModel(model_name)
        except ImportError:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
    
    def _init_openai(self):
        """Initialize OpenAI"""
        try:
            from openai import OpenAI
            api_key = current_app.config.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not configured")
            return OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai")
    
    def _init_anthropic(self):
        """Initialize Anthropic Claude"""
        try:
            from anthropic import Anthropic
            api_key = current_app.config.get('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            return Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic not installed. Run: pip install anthropic")
    
    def _init_groq(self):
        """Initialize Groq"""
        try:
            from groq import Groq
            api_key = current_app.config.get('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY not configured")
            return Groq(api_key=api_key)
        except ImportError:
            raise ImportError("groq not installed. Run: pip install groq")
    
    def generate_response(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Dict:
        """
        Generate AI response from conversation history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt for context
        
        Returns:
            Dict with 'content', 'model', and 'tokens_used'
        """
        if self.provider == 'gemini':
            return self._generate_gemini(messages, system_prompt)
        elif self.provider == 'openai':
            return self._generate_openai(messages, system_prompt)
        elif self.provider == 'anthropic':
            return self._generate_anthropic(messages, system_prompt)
        elif self.provider == 'groq':
            return self._generate_groq(messages, system_prompt)
    
    def _generate_gemini(self, messages: List[Dict], system_prompt: Optional[str]) -> Dict:
        """Generate response using Google Gemini"""
        # Build conversation history for Gemini
        chat_history = []
        for msg in messages[:-1]:  # All except last message
            role = 'user' if msg['role'] == 'user' else 'model'
            chat_history.append({'role': role, 'parts': [msg['content']]})
        
        # Start chat with history
        chat = self.client.start_chat(history=chat_history)
        
        # Send last message
        last_message = messages[-1]['content']
        
        # Add system prompt if provided
        if system_prompt:
            last_message = f"{system_prompt}\n\nUser: {last_message}"
        
        response = chat.send_message(last_message)
        
        return {
            'content': response.text,
            'model': self.model_name,
            'tokens_used': getattr(response, 'usage_metadata', {}).get('total_token_count', 0)
        }
    
    def _generate_openai(self, messages: List[Dict], system_prompt: Optional[str]) -> Dict:
        """Generate response using OpenAI"""
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({'role': 'system', 'content': system_prompt})
        
        formatted_messages.extend(messages)
        
        response = self.client.chat.completions.create(
            model=self.model_name or 'gpt-4-turbo-preview',
            messages=formatted_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return {
            'content': response.choices[0].message.content,
            'model': response.model,
            'tokens_used': response.usage.total_tokens
        }
    
    def _generate_anthropic(self, messages: List[Dict], system_prompt: Optional[str]) -> Dict:
        """Generate response using Anthropic Claude"""
        response = self.client.messages.create(
            model=self.model_name or 'claude-3-opus-20240229',
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt or "You are a compassionate mental health support assistant.",
            messages=messages
        )
        
        return {
            'content': response.content[0].text,
            'model': response.model,
            'tokens_used': response.usage.input_tokens + response.usage.output_tokens
        }
    
    def _generate_groq(self, messages: List[Dict], system_prompt: Optional[str]) -> Dict:
        """Generate response using Groq"""
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({'role': 'system', 'content': system_prompt})
        
        formatted_messages.extend(messages)
        
        response = self.client.chat.completions.create(
            model=self.model_name or 'mixtral-8x7b-32768',
            messages=formatted_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return {
            'content': response.choices[0].message.content,
            'model': response.model,
            'tokens_used': response.usage.total_tokens
        }
    
    def get_empathetic_system_prompt(self) -> str:
        """Get the system prompt for empathetic mental health support"""
        return """You are a compassionate and empathetic mental health support assistant. Your role is to:

1. Listen actively and validate the user's feelings
2. Provide emotional support and encouragement
3. Ask clarifying questions to better understand their situation
4. Suggest evidence-based coping strategies (CBT, DBT, mindfulness)
5. Encourage professional help when appropriate
6. Maintain boundaries - you are a support tool, not a replacement for therapy

Guidelines:
- Use warm, non-judgmental language
- Avoid giving direct medical advice
- Be culturally sensitive
- Recognize crisis situations and provide appropriate resources
- Encourage self-care and healthy habits
- Validate emotions while promoting positive coping

Remember: Your goal is to provide support, not diagnosis or treatment."""


# Singleton instance
_ai_connector = None


def get_ai_connector() -> AIConnector:
    """Get or create AI connector singleton"""
    global _ai_connector
    if _ai_connector is None:
        _ai_connector = AIConnector()
    return _ai_connector
