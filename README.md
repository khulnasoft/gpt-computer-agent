# GPT Computer Agent
Hi, this is an alternative work for providing ChatGPT MacOS app to Windows and Linux. In this way this is a fresh and stable work. You can easily install as Python library for this time but we will prepare a pipeline for providing native install scripts (.exe).

<p align="start">
  <br>
     <a href="https://github.com/khulnasoft/gpt-computer-agent/releases/latest/download/GPT_Computer_Agent_windows.exe">
   <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="windows">
   </a>
   <a href="https://github.com/khulnasoft/gpt-computer-agent/releases/latest/download/GPT_Computer_Agent_macos">
   <img src="https://img.shields.io/badge/mac%20os-000000?style=for-the-badge&logo=apple&logoColor=white" alt="macos">
   </a>
    <a href="https://github.com/khulnasoft/gpt-computer-agent?tab=readme-ov-file#agent-installation-and-run">
   <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="linux">
   </a>
  <br>
  <br> 

  </p>


## Developer Installation and Run
Needed >= Python 3.9
```console
pip3 install gpt-computer-agent[default]
```

```console
computeragent
```

### Assistant Infrastructure | NEW

With this way you can create `crewai` agents and using it into gpt-computer-agent gui and tools.


```console
pip3 install gpt-computer-agent[default]
pip3 install gpt-computer-agent[assistantc]
```

```python
from gpt_computer_agent import Assistant, start

manager = Assistant(
  role='Project Manager',
  goal='understands project needs and assist coder',
  backstory="""You're a manager at a large company.""",
)

coder = Assistant(
  role='Senior Python Coder',
  goal='writing python scripts and copying to clipboard',
  backstory="""You're a python developer at a large company.""",
)


start()
```


### Adding Custom Tools | NEW

Now you are able to add custom tools that run in the assistantc infra and agent processes. 


```python
from gpt_computer_agent import Tool, start

@Tool
def sum_tool(first_number: int, second_number: int) -> str:
    """Useful for when you need to sum two numbers together."""
    return first_number + second_number

start()
```

## Capabilities
At this time we have many infrastructure elements. We just aim to provide whole things that already in ChatGPT app.


| Capability                         | Description                      |
|------------------------------------|----------------------------------|
| **Screen Read**                    |            OK                    |
| **Click to and Text or Icon in the screen**                    |            OK                    |
| **Microphone**                     |            OK                    |
| **System Audio**                  |            OK                    |
| **Memory**                         |            OK                    |
| **Open and Close App**             |            OK                    |
| **Open a URL**                     |            OK                    |
| **Clipboard**                       |            OK                    |
| **Search Engines**                 |            OK                    |
| **Writing and running Python**     |            OK                    |
| **Writing and running SH**    |            OK                    |
| **Using your Telegram Account**    |            OK                    |
| **Knowledge Management**           |            OK                    |
