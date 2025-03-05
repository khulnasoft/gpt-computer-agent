try:
    from ..llm import get_model
    from ..utils.db import *
    from ..llm_settings import llm_settings
    from ..tooler import *
    from ..display_tools import *
    from ..cu.computer import *
    from ..teams import *
    from .agent_tools import get_tools
    from ..mcp.tool import mcp_tools
    from ..standard_tools import get_standard_tools

except ImportError:
    from llm import get_model
    from utils.db import *
    from llm_settings import llm_settings
    from tooler import *
    from display_tools import *
    from cu.computer import *
    from teams import *
    from agent.agent_tools import get_tools
    from mcp.tool import mcp_tools
    from standard_tools import get_standard_tools


from langgraph.prebuilt import create_react_agent


custom_tools_ = []


def custom_tools():
    global custom_tools_
    the_list = []
    the_list += custom_tools_
    return the_list


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


def get_agent_executor(the_anthropic_model=False, no_tools=False):
    tools = get_tools()
    tools += custom_tools()

    model = load_model_settings()

    if is_predefined_agents_setting_active() and llm_settings[model]["tools"]:
        try:
            import crewai

            tools += [search_on_internet_and_report_team, generate_code_with_aim_team]
        except ImportError:
            pass

    if the_anthropic_model:
        tools += []
        if load_aws_access_key_id() == "default":
            model_catch = get_model(the_model="claude-3-5-sonnet-20241022")
        else:
            model_catch = get_model(
                the_model="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
            )

        print("Anthropic model catch", model_catch)
        print("Anthropic tools len", len(tools))
        return create_react_agent(model_catch, tools)
    else:
        tools += (
            [mouse_scroll, click_to_text, click_to_icon, click_to_area]
            + mcp_tools()
            + get_standard_tools()
        )

    if no_tools:
        tools = []

    return create_react_agent(get_model(), tools)
