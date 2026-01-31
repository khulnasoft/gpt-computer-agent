# Tool Integration Example

Advanced examples of tool integration with the GPT structure, including custom tools, tool chaining, and complex workflows.

## 🎯 **Features:**

- Custom tool creation
- Tool chaining and workflows
- File system tools
- Web scraping tools
- Database integration
- API integration tools
- Tool error handling
- Parallel tool execution

## 📋 **Requirements:**

- Python 3.10+
- OpenAI API key
- Various API keys (depending on tools used)

## 🚀 **Setup:**

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export OPENAI_API_KEY="your-api-key-here"
export WEATHER_API_KEY="your-weather-api-key"  # Optional
export NEWS_API_KEY="your-news-api-key"        # Optional
```

3. Run the example:
```bash
python main.py
```

## 🔧 **Available Tools:**

### File Operations
- Read/write files
- Directory operations
- File search

### Web Tools
- Web scraping
- API calls
- URL validation

### Data Tools
- JSON processing
- CSV operations
- Data analysis

### System Tools
- System information
- Process management
- Network tools

## 💡 **Examples:**

- "Read the file config.yaml and tell me what's in it"
- "Scrape the headlines from news.example.com"
- "Calculate the result of 15 * 8 + 12"
- "Search for all Python files in the current directory"
