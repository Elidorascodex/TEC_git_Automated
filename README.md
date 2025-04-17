# AIRTH System (Automated Intelligence for The Elidoras Codex)

## Overview
AIRTH is an advanced content automation system that generates and publishes content directly to The Elidoras Codex WordPress site. It combines multiple AI models (GPT-4, Claude) for rich content generation with direct WordPress integration.

## Features
- Multi-model article generation using OpenAI and Anthropic
- Direct WordPress publishing via XML-RPC
- Asynchronous batch processing
- Configurable content categories and tags
- Error handling and monitoring

## Setup

### 1. Environment Setup
Create a `.env` file with your credentials:
```env
# API Keys
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# WordPress Configuration
WP_SITE_URL=https://elidorascodex.com
WP_USER=your_username
WP_APP_PASSWORD=your_app_password
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configuration
Adjust `config.yaml` for your needs:
- Set batch processing limits
- Configure model preferences
- Adjust WordPress posting defaults

## Usage

### Running the System
```bash
python services/orchestrator.py
```

### Adding Topics
Modify the topics list in `orchestrator.py` or create a separate topics file.

### Checking Results
All posts are created as drafts by default. Check your WordPress dashboard to review and publish.

## Structure
```
TEC_git_Automated/
├── services/
│   ├── article-generator/
│   │   └── main.py
│   ├── content-poster/
│   │   └── wordpress_handler.py
│   └── orchestrator.py
├── config.yaml
├── requirements.txt
└── .env
```

## Error Handling
- All errors are logged with timestamps
- Failed generations are reported but don't stop batch processing
- WordPress connection issues are handled gracefully

## Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License
See LICENSE file for details