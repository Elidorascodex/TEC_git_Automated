import asyncio
import os
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

# Import our service modules
from services.article_generator.main import ArticleGenerator
from services.content_poster.wordpress_handler import WordPressHandler

load_dotenv()

class AIRTHOrchestrator:
    def __init__(self):
        self.article_generator = ArticleGenerator()
        self.wordpress_handler = WordPressHandler()

    async def process_topic(self, topic: str, context: Dict = None) -> Dict:
        """Process a single topic through the AIRTH pipeline"""
        try:
            # Generate article content
            content = await self.article_generator.generate_article(topic, context)
            
            # Format title
            title = f"AIRTH Analysis: {topic}"
            
            # Post to WordPress as draft
            post_result = await self.wordpress_handler.create_post(
                title=title,
                content=content,
                status='draft',
                categories=['AI Analysis', 'AIRTH'],
                tags=['ai-generated', 'airth', 'analysis']
            )
            
            return {
                'status': 'success',
                'post_id': post_result['id'],
                'post_url': post_result['url'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def process_batch(self, topics: List[str]) -> List[Dict]:
        """Process multiple topics in parallel"""
        tasks = [self.process_topic(topic) for topic in topics]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

async def main():
    orchestrator = AIRTHOrchestrator()
    
    # Example usage
    topics = [
        "The intersection of mythology and technology",
        "Digital immortality through AI",
        "Modern grimoires in the age of algorithms"
    ]
    
    results = await orchestrator.process_batch(topics)
    for result in results:
        print(f"Processing result: {result}")

if __name__ == "__main__":
    asyncio.run(main())