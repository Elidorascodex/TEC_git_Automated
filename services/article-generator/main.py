from typing import Dict, Any
import os
from dotenv import load_dotenv
import openai
from google.cloud import aiplatform
import anthropic
import json

load_dotenv()

class ArticleGenerator:
    def __init__(self):
        self.openai_client = openai.Client(api_key=os.getenv('OPENAI_API_KEY'))
        self.anthropic_client = anthropic.Client(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
    async def generate_article(self, topic: str, context: Dict[Any, Any] = None) -> str:
        """Generate article content using multiple AI models for diversity and depth"""
        
        # OpenAI (GPT-4) generation
        openai_response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert content writer for The Elidoras Codex."},
                {"role": "user", "content": f"Write an article about: {topic}"}
            ]
        )
        
        # Anthropic (Claude) generation for additional perspective
        claude_response = await self.anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": f"Write a detailed article about {topic} in the style of The Elidoras Codex"
            }]
        )
        
        # Combine and enhance the content
        combined_content = self._merge_and_enhance_content(
            openai_response.choices[0].message.content,
            claude_response.content
        )
        
        return combined_content
    
    def _merge_and_enhance_content(self, content1: str, content2: str) -> str:
        """Merge and enhance content from different AI models"""
        # Add your content merging logic here
        # For now, we'll use a simple combination
        return f"{content1}\n\n---\n\nAlternative Perspective:\n{content2}"

if __name__ == "__main__":
    generator = ArticleGenerator()
    # Add your test code here