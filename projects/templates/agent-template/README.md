# Agent Template

A template for creating new GPT agents with the Aideck framework.

## 📁 **Structure:**

```
agent-template/
├── README.md           # This file
├── main.py            # Main agent implementation
├── requirements.txt   # Dependencies
├── config/
│   └── config.yaml    # Configuration file
├── tools/
│   ├── __init__.py    # Tools package
│   └── custom_tools.py # Custom tools
└── tests/
    ├── __init__.py    # Tests package
    └── test_agent.py  # Agent tests
```

## 🚀 **Getting Started:**

1. Copy this template to a new directory
2. Customize the agent configuration
3. Add your custom tools
4. Implement your agent logic
5. Write tests

## 📝 **Customization:**

- Edit `config/config.yaml` for configuration
- Add tools in `tools/custom_tools.py`
- Modify `main.py` for agent behavior
- Write tests in `tests/test_agent.py`

## 🔧 **Configuration:**

See `config/config.yaml` for available options.

## 🧪 **Testing:**

Run tests with:
```bash
python -m pytest tests/
```
