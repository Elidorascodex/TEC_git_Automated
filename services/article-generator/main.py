from typing import Dict, Any
import os
from dotenv import load_dotenv
import openai
from google.cloud import aiplatform
import anthropic
import json
import yaml
import asyncio
from datetime import datetime

load_dotenv()

class ArticleGenerator:
    def __init__(self):
        # Load config
        with open('config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        # Initialize AI clients
        self.openai_client = openai.Client(api_key=os.getenv('OPENAI_API_KEY'))
        self.anthropic_client = anthropic.Client(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
    async def generate_article(self, topic: str, context: Dict[Any, Any] = None) -> Dict[str, Any]:
        """Generate article content using multiple AI models for depth and perspective"""
        try:
            # OpenAI (GPT-4) generation
            openai_response = await self._generate_with_openai(topic, context)
            
            # Anthropic (Claude) generation
            claude_response = await self._generate_with_anthropic(topic, context)
            
            # Gemini generation for additional perspective
            gemini_response = await self._generate_with_gemini(topic, context)
            
            # Combine and enhance content
            final_content = self._merge_and_enhance_content(
                openai_response,
                claude_response,
                gemini_response
            )
            
            return {
                'status': 'success',
                'content': final_content,
                'metadata': {
                    'topic': topic,
                    'timestamp': datetime.now().isoformat(),
                    'models_used': ['gpt-4', 'claude-3', 'gemini-pro'],
                    'context_used': bool(context)
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'topic': topic,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _generate_with_openai(self, topic: str, context: Dict[Any, Any] = None) -> str:
        """Generate content using OpenAI's GPT-4"""
        prompt = self._create_prompt(topic, context)
        response = await self.openai_client.chat.completions.create(
            model=self.config['ai_services']['openai']['model'],
            messages=[
                {"role": "system", "content": "You are an expert content writer for The Elidoras Codex, specializing in mythology, technology, and their intersection."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.config['ai_services']['openai']['max_tokens'],
            temperature=self.config['ai_services']['openai']['temperature']
        )
        return response.choices[0].message.content
    
    async def _generate_with_anthropic(self, topic: str, context: Dict[Any, Any] = None) -> str:
        """Generate content using Anthropic's Claude"""
        prompt = self._create_prompt(topic, context)
        response = await self.anthropic_client.messages.create(
            model=self.config['ai_services']['anthropic']['model'],
            max_tokens=self.config['ai_services']['anthropic']['max_tokens'],
            messages=[{
                "role": "user",
                "content": f"Write a detailed article for The Elidoras Codex about {prompt}"
            }]
        )
        return response.content
    
    async def _generate_with_gemini(self, topic: str, context: Dict[Any, Any] = None) -> str:
        """Generate content using Google's Gemini"""
        # Initialize Gemini
        aiplatform.init(project=os.getenv('GOOGLE_CLOUD_PROJECT'))
        
        prompt = self._create_prompt(topic, context)
        model = aiplatform.Model(f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/models/gemini-pro")
        
        response = model.predict(prompt)
        return response.text
    
    def _create_prompt(self, topic: str, context: Dict[Any, Any] = None) -> str:
        """Create a detailed prompt for article generation"""
        base_prompt = f"Write an in-depth article about {topic} for The Elidoras Codex. "
        base_prompt += "Focus on the intersection of mythology, technology, and human experience. "
        
        if context:
            if 'style' in context:
                base_prompt += f"\nStyle: {context['style']}"
            if 'themes' in context:
                base_prompt += f"\nKey themes to explore: {', '.join(context['themes'])}"
            if 'references' in context:
                base_prompt += f"\nInclude references to: {', '.join(context['references'])}"
                
        return base_prompt
    
    def _merge_and_enhance_content(self, content1: str, content2: str, content3: str) -> str:
        """Merge and enhance content from different AI models"""
        # Create sections from each model's content
        sections = [
            "## Main Analysis\n" + content1,
            "## Alternative Perspective\n" + content2,
            "## Additional Insights\n" + content3
        ]
        
        # Combine with proper formatting
        merged_content = "\n\n".join(sections)
        
        # Add metadata footer
        footer = f"\n\n---\n*This article was generated by AIRTH using multiple AI models, " \
                f"combining perspectives from GPT-4, Claude, and Gemini Pro. " \
                f"Generated on {datetime.now().strftime('%Y-%m-%d')}*"
                
        return merged_content + footer

async def main():
    """Test the article generator"""
    generator = ArticleGenerator()
    test_topic = "The intersection of ancient Norse runes and modern cryptography"
    test_context = {
        'style': 'academic but accessible',
        'themes': ['digital security', 'historical preservation', 'modern applications'],
        'references': ['Elder Futhark', 'blockchain', 'zero-knowledge proofs']
    }
    
    result = await generator.generate_article(test_topic, test_context)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())