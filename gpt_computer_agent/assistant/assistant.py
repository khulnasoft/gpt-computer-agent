try:
    from ..llm import get_model
    from ..utils.db import *
    from ..llm_settings import llm_settings
    from ..tooler import click_on_a_text_on_the_screen, click_on_a_icon_on_the_screen, search_on_internet_and_report_team
except ImportError:
    from llm import get_model
    from utils.db import *
    from llm_settings import llm_settings
    from tooler import click_on_a_text_on_the_screen, click_on_a_icon_on_the_screen, search_on_internet_and_report_team


from langgraph.checkpoint.sqlite import SqliteSaver


from langchain.assistants import AssistantExecutor, create_json_chat_assistant


from langgraph.prebuilt import chat_assistant_executor


custom_tools = []



def load_tiger_tools():
    try:
        from upsonic import Tiger
        tools = Tiger()
        tools.enable_auto_requirements = True
        tools = tools.langchain()
        return tools
    except:
        return False


def load_default_tools():
    from ..standard_tools import the_standard_tools
    return the_standard_tools


prompt_cache = {}


def get_prompt(name):
    global prompt_cache
    if name in prompt_cache:
        return prompt_cache[name]
    else:
        from langchain import hub

        prompt = hub.pull(name)
        prompt_cache[name] = prompt
        return prompt


def get_tools():
    if is_online_tools_setting_active():
        tools = load_tiger_tools()
        if not tools:
            tools = load_default_tools()
    else:
        tools = load_default_tools()
    return tools


def get_assistant_executor():
    global custom_tools
    tools = get_tools()
    tools += custom_tools

    if is_predefined_assistants_setting_active():
        try:
            import crewai
            tools += [search_on_internet_and_report_team]
        except ImportError:
            pass


    model = load_model_settings()


    if llm_settings[model]["provider"] == "openai":
        tools += [click_on_a_text_on_the_screen, click_on_a_icon_on_the_screen]


    if llm_settings[model]["provider"] == "openai" or llm_settings[model]["provider"] == "groq":
        return chat_assistant_executor.create_tool_calling_executor(get_model(), tools)



    if llm_settings[model]["provider"] == "ollama":
        from langchain import hub

        prompt = get_prompt("hwchase17/react-chat-json")
        the_assistant = create_json_chat_assistant(get_model(), tools, prompt)
        return AssistantExecutor(
            assistant=the_assistant, tools=tools, verbose=True, handle_parsing_errors=True
        )





"""
from langchain.assistants import Tool
from langchain_experimental.utilities import PythonREPL
python_repl = PythonREPL()
# You can create the tool to pass to an assistant
repl_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
    func=python_repl.run,
)

from langgraph.prebuilt import chat_assistant_executor
def get_assistant_executor():
    return chat_assistant_executor.create_tool_calling_executor(get_model(), [repl_tool])
"""
