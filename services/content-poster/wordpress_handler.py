import os
from typing import Dict, Optional
import requests
from dotenv import load_dotenv
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, EditPost
from wordpress_xmlrpc.methods.media import UploadFile

load_dotenv()

class WordPressHandler:
    def __init__(self):
        self.wp_url = os.getenv('WP_SITE_URL')
        self.wp_user = os.getenv('WP_USER')
        self.wp_app_password = os.getenv('WP_APP_PASSWORD')
        self.xmlrpc_url = f"{self.wp_url}/xmlrpc.php"
        self.client = Client(self.xmlrpc_url, self.wp_user, self.wp_app_password)

    async def create_post(self, 
                         title: str, 
                         content: str, 
                         status: str = 'draft',
                         categories: Optional[list] = None,
                         tags: Optional[list] = None) -> Dict:
        """Create a new WordPress post"""
        post = WordPressPost()
        post.title = title
        post.content = content
        post.post_status = status
        
        if categories:
            post.terms_names = {'category': categories}
        if tags:
            post.terms_names = {'post_tag': tags}

        # Create the post
        post_id = self.client.call(NewPost(post))
        
        return {
            'id': post_id,
            'status': status,
            'url': f"{self.wp_url}/?p={post_id}"
        }

    async def update_post(self, 
                         post_id: int, 
                         title: Optional[str] = None,
                         content: Optional[str] = None,
                         status: Optional[str] = None) -> Dict:
        """Update an existing WordPress post"""
        post = WordPressPost()
        post.id = post_id
        
        if title:
            post.title = title
        if content:
            post.content = content
        if status:
            post.post_status = status

        success = self.client.call(EditPost(post_id, post))
        
        return {
            'id': post_id,
            'success': success,
            'status': status if status else 'unchanged'
        }

    async def upload_media(self, file_path: str, filename: Optional[str] = None) -> Dict:
        """Upload media to WordPress"""
        with open(file_path, 'rb') as img:
            data = {
                'name': filename or os.path.basename(file_path),
                'type': self._get_mime_type(file_path),
                'bits': img.read()
            }
            
            response = self.client.call(UploadFile(data))
            return response

    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf'
        }
        return mime_types.get(ext, 'application/octet-stream')