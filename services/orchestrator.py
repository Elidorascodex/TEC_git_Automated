import asyncio
import os
from datetime import datetime
import yaml
from typing import Dict, List, Any
from dotenv import load_dotenv
from article_generator.main import ArticleGenerator
from content_poster.wordpress_handler import WordPressHandler
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AIRTH_Orchestrator')

class AIRTHOrchestrator:
    def __init__(self):
        load_dotenv()
        
        # Load configuration
        with open('config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.article_generator = ArticleGenerator()
        self.wordpress_handler = WordPressHandler()
        
    async def process_topic(self, topic: str, context: Dict = None) -> Dict:
        """Process a single topic through the AIRTH pipeline"""
        try:
            logger.info(f"Starting processing for topic: {topic}")
            
            # Generate article content
            generation_start = datetime.now()
            article_result = await self.article_generator.generate_article(topic, context)
            generation_time = (datetime.now() - generation_start).total_seconds()
            
            if article_result['status'] != 'success':
                raise Exception(f"Article generation failed: {article_result.get('error')}")
            
            # Format title
            title = f"AIRTH Analysis: {topic}"
            
            # Post to WordPress as draft
            posting_start = datetime.now()
            post_result = await self.wordpress_handler.create_post(
                title=title,
                content=article_result['content'],
                status='draft',
                categories=self.config['wordpress']['default_categories'],
                tags=self.config['wordpress']['default_tags']
            )
            posting_time = (datetime.now() - posting_start).total_seconds()
            
            return {
                'status': 'success',
                'post_id': post_result['id'],
                'post_url': post_result['url'],
                'metrics': {
                    'generation_time': generation_time,
                    'posting_time': posting_time,
                    'total_time': generation_time + posting_time
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing topic {topic}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'topic': topic,
                'timestamp': datetime.now().isoformat()
            }

    async def process_batch(self, topics: List[str], contexts: List[Dict] = None) -> List[Dict]:
        """Process multiple topics in parallel"""
        if not contexts:
            contexts = [None] * len(topics)
            
        batch_size = self.config['content_generation']['batch_size']
        results = []
        
        for i in range(0, len(topics), batch_size):
            batch_topics = topics[i:i + batch_size]
            batch_contexts = contexts[i:i + batch_size]
            
            # Process batch in parallel
            tasks = [self.process_topic(topic, context) 
                    for topic, context in zip(batch_topics, batch_contexts)]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)
            
            # Apply cooldown between batches if more remain
            if i + batch_size < len(topics):
                cooldown = self.config['content_generation']['cooldown_minutes'] * 60
                logger.info(f"Cooling down for {cooldown} seconds before next batch")
                await asyncio.sleep(cooldown)
                
        return results

    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics"""
        return {
            'system_name': self.config['system']['name'],
            'version': self.config['system']['version'],
            'timestamp': datetime.now().isoformat(),
            'config': {
                'batch_size': self.config['content_generation']['batch_size'],
                'cooldown': self.config['content_generation']['cooldown_minutes'],
                'max_daily_posts': self.config['content_generation']['max_daily_posts']
            }
        }

async def main():
    """Example usage of the AIRTH orchestrator"""
    orchestrator = AIRTHOrchestrator()
    
    # Example topics and contexts
    topics = [
        "The intersection of mythology and blockchain technology",
        "Digital immortality through AI and ancient Egyptian preservation techniques",
        "Modern grimoires: Programming languages as magical systems"
    ]
    
    contexts = [
        {
            'style': 'academic',
            'themes': ['technology', 'mythology', 'decentralization'],
            'references': ['Bitcoin', 'Norse mythology', 'smart contracts']
        },
        {
            'style': 'exploratory',
            'themes': ['preservation', 'digital consciousness', 'immortality'],
            'references': ['mummification', 'neural networks', 'consciousness uploading']
        },
        {
            'style': 'technical-mystical',
            'themes': ['programming', 'occult knowledge', 'modern magic'],
            'references': ['compiler theory', 'hermetic principles', 'software patterns']
        }
    ]
    
    # Process the batch
    results = await orchestrator.process_batch(topics, contexts)
    
    # Print results
    for result in results:
        if result['status'] == 'success':
            logger.info(f"Successfully processed article: {result['post_url']}")
        else:
            logger.error(f"Failed to process article: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())