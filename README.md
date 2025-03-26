# Twitter Manager

An automated Twitter bot that generates and posts tech-focused content using AI. The bot uses HuggingFace's models to generate informative tweets about programming, software development, and tech best practices.

## Features

- 🤖 AI-powered tweet generation using HuggingFace models
- 📊 SQLite database for tracking post history
- 📅 Automated hourly posting via GitHub Actions
- 🔄 Automatic retries and error handling
- 📝 Comprehensive logging
- ⚡ Rate limit management
- 🎯 Content appropriateness validation
- 🔍 Duplicate content detection

## Requirements

- Python 3.8 or higher
- Twitter Developer Account with API credentials
- Sufficient disk space for model storage
- Internet connection for API access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/twitter_manager.git
cd twitter_manager
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Copy the example env file
cp .env.example .env
```

5. Edit the `.env` file with your Twitter API credentials:
```
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

## GitHub Actions Setup

The bot runs automatically every 6 hours using GitHub Actions. To set this up:

1. Go to your repository's Settings > Secrets and variables > Actions
2. Add the following repository secrets:
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`

The workflow is defined in `.github/workflows/twitter-scheduler.yml` and will:
- Run every 6 hours automatically
- Can be triggered manually via the Actions tab
- Handle all Twitter posting operations

## Usage

### Manual Running

To run the Twitter Manager manually:

```bash
python -m src.twitter_manager
```

The bot will:
- Initialize all components
- Validate configurations
- Post a tweet immediately
- Log all activities to `logs/twitter_manager.log`

### Configuration

You can modify the following settings in `src/config.py`:

- `MODEL_NAME`: HuggingFace model to use
- `TOPICS`: List of tech topics to tweet about
- `MAX_RETRIES`: Number of retry attempts
- `MAX_TWEETS_PER_DAY`: Daily tweet limit

### Database

The SQLite database (`data/twitter.db`) tracks:
- Posted content
- Posting timestamps
- Success/failure status
- Error messages

### Logs

Logs are stored in `logs/twitter_manager.log` and include:
- Initialization status
- Post attempts and results
- Errors and exceptions
- Rate limit information

## Project Structure

```
twitter_manager/
├── .github/
│   └── workflows/           # GitHub Actions workflows
│       ├── heroku-deploy.yml    # Deployment workflow
│       └── twitter-scheduler.yml # Scheduling workflow
├── src/
│   ├── __init__.py
│   ├── twitter_manager.py    # Main orchestration script
│   ├── content_generator.py  # AI content generation
│   ├── twitter_handler.py    # Twitter API integration
│   ├── db_manager.py        # Database operations
│   └── config.py            # Configuration settings
├── data/
│   └── twitter.db           # SQLite database
├── logs/
│   └── twitter_manager.log  # Application logs
├── tests/
│   └── test_*.py           # Test files
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment variables
└── README.md               # This file
```

## Error Handling

The system handles various error cases:
- Twitter API rate limits
- Network connectivity issues
- Content generation failures
- Database errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is intended for educational purposes. Ensure compliance with Twitter's terms of service and API usage guidelines when deploying.