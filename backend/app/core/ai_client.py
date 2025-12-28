"""
Groq API client for AI chat functionality
OpenAI-compatible API interface
"""
import aiohttp
import json
from typing import List, Dict, Any, AsyncGenerator
from app.config import settings


class GroqClient:
    """Groq API client wrapper"""

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = settings.GROQ_MODEL

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """Send chat completion request to Groq"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:

                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Groq API error: {response.status} - {error_text}")

                if stream:
                    # Handle streaming response
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data = line[6:]  # Remove 'data: ' prefix
                            if data == '[DONE]':
                                break

                            try:
                                chunk = json.loads(data)
                                if chunk.get('choices'):
                                    content = chunk['choices'][0].get('delta', {}).get('content', '')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
                else:
                    # Handle non-streaming response
                    result = await response.json()
                    content = result['choices'][0]['message']['content']
                    yield content

    async def create_embedding(self, text: str) -> List[float]:
        """Create embeddings for text (if needed for custom implementations)"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "text-embedding-ada-002",  # Groq supports OpenAI-compatible models
            "input": text
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json=payload
            ) as response:

                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Groq embedding error: {response.status} - {error_text}")

                result = await response.json()
                return result['data'][0]['embedding']


# Global AI client instance
ai_client = GroqClient()


def get_ai_client():
    """Get the global AI client instance"""
    return ai_client


