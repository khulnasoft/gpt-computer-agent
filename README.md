# GPT Computer Agent
Hi, this is an alternative work for providing ChatGPT MacOS app to Windows and Linux. In this way this is a fresh and stable work. You can easily install as Python library for this time but we will prepare a pipeline for providing native install scripts (.exe).

Powered by <a href="https://github.com/Upsonic/Tiger"><strong>Upsonic Tiger 🐅</strong></a> A function hub for llm agents.




## Installation and Run
Needed >= Python 3.9
```console
pip3 install 'gpt-computer-agent[base]'
```

```console
computeragent
```

### Wake Word | NEW
<details>


We have added Pvporcupine integration. To use it, you need to install an additional library:

```console
pip3 install 'gpt-computer-agent[wakeword]'
```

After that, please enter your [Pvporcupine](https://picovoice.ai/) API key and enable the wake word feature.
</details>

<p align="center">
<br>
  <br>
  <br>

</p>


### Agent Infrastructure

With this way you can create `crewai` agents and using it into gpt-computer-agent gui and tools.


```console
pip3 install 'gpt-computer-agent[base]'
pip3 install 'gpt-computer-agent[agentic]'
```

```python
from gpt_computer_agent import Agent, start

manager = Agent(
  role='Project Manager',
  goal='understands project needs and assist coder',
  backstory="""You're a manager at a large company.""",
)

coder = Agent(
  role='Senior Python Coder',
  goal='writing python scripts and copying to clipboard',
  backstory="""You're a python developer at a large company.""",
)


start()
```



### Adding Custom Tools

Now you are able to add custom tools that run in the agentic infra and agent processes. 


```python
from gpt_computer_agent import Tool, start

@Tool
def sum_tool(first_number: int, second_number: int) -> str:
    """Useful for when you need to sum two numbers together."""
    return first_number + second_number

start()
```






### API | NEW

Now you can use your GPT Computer Agent remotely! GUI still active, for this there is few steps:

```console
pip3 install 'gpt-computer-agent[base]'
pip3 install 'gpt-computer-agent[api]'
```

```console
computeragent --api
```


```python
from gpt_computer_agent.remote import remote

output = remote.input("Hi, how are you today?", screen=False, talk=False)
print(output)

remote.just_screenshot()

remote.talk("TTS test")

# Other Functionalities
remote.reset_memory()
remote.profile("default")

remote.enable_predefined_agents()
remote.disable_predefined_agents()

remote.enable_online_tools()
remote.disable_online_tools()
```






<p align="center">
<br>
  <br>
  <br>
  <br>
  <br>
</p>

## Roadmap
| Feature                         | Status       | Target Release |
|---------------------------------|--------------|----------------|
| Clear Chat History         | Completed    | Q2 2024        |
| Long Audios Support (Split 20mb)      | Completed    | Q2 2024        |
| Text Inputs               | Completed      | Q2 2024        |
| Just Text Mode (Mute Speech)           | Completed  | Q2 2024        |
| Added profiles (Different Chats)          | Completed    | Q2 2024        |
| More Feedback About Agent Status                  | Completed    | Q2 2024        |
| Local Model Vision and Text (With Ollama, and vision models)  | Completed  | Q2 2024        |
| **Our Customizable Agent Infrastructure**              | Completed      | Q2 2024        |
| Supporting Groq Models  | Completed  | Q2 2024        |
| **Adding Custom Tools**  | Completed  | Q2 2024        |
| Click on something on the screen (text and icon)              | Completed      | Q2 2024        |
| New UI              | Completed      | Q2 2024        |
| Native Applications, exe, dmg              | Failed (Agentic Infra libraries not supported for now)     | Q2 2024        |
| **Collaborated Speaking Different Voice Models on long responses.**              | Completed     | Q2 2024        |
| **Auto Stop Recording, when you complate talking**              | Completed     | Q2 2024        |
| **Wakeup Word**              | Completed     | Q2 2024        |
| **Continuously Conversations**              | Completed     | Q2 2024        |
| **Adding more capability on device**              | Planned     | Q2 2024        |
| DeepFace Integration (Facial Recognition)                    | Planned  | Q2 2024        |







## Capabilities
At this time we have many infrastructure elements. We just aim to provide whole things that already in ChatGPT app.

| Capability                         | Status                      |
|------------------------------------|----------------------------------|
| **Screen Read**                    |            OK                    |
| **Click to and Text or Icon in the screen**                    |            OK                    |
| **Move to and Text or Icon in the screen**                    |            OK                    |
| **Typing Something**                    |            OK                    |
| **Pressing to Any Key**                    |            OK                    |
| **Scrolling**                    |            OK                    |
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
| **[Add more tool](https://github.com/khulnasoft/gpt-computer-agent/blob/master/gpt_computer_agent/standard_tools.py)**           |            ?                    |

### Predefined Agents
If you enable it your agent will work with these teams:

| Team Name                         | Status                      |
|------------------------------------|----------------------------------|
| **search_on_internet_and_report_team**                    |            OK                    |
| **generate_code_with_aim_team_**                    |            OK                    |
| **[Add your own one](https://github.com/khulnasoft/gpt-computer-agent/blob/master/gpt_computer_agent/teams.py)**                    |            ?                    |


## Contributors

<a href="https://github.com/khulnasoft/gpt-computer-agent/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=khulnasoft/gpt-computer-agent" />
</a>
