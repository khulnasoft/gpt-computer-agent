import traceback

from langchain_core.messages import HumanMessage

try:

    from ..agent import get_agent_executor
    from ..llm import get_model
    from ..llm_settings import llm_settings
    from ..screen.shot import *
    from ..utils.chat_history import ChatHistory
    from ..utils.db import agents, load_model_settings
    from .computer import screenshot_action
except ImportError:

    from computer import screenshot_action
    from screen.shot import *


def ask_anthropic(the_request: str):

    try:

        from ..agent import get_agent_executor
    except ImportError:
        from agent import get_agent_executor

    try:
        print("ASK ANTHROPIC", the_request)

        llm_input = the_request

        print("LLM INPUT", llm_input)

        human_first_message = {"type": "text", "text": f"{llm_input}"}

        the_message = [human_first_message]

        human_second_message = None

        base64_image = screenshot_action(direct_base64=True)

        human_second_message = {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_image}"},
        }

        print("LEN OF IMAGE", len(base64_image))

        if human_second_message:
            the_message.append(human_second_message)

        the_message = HumanMessage(content=the_message)

        msg = get_agent_executor(the_anthropic_model=True).invoke(
            {"messages": [the_message]}
        )

        the_last_messages = msg["messages"]

        return_value = the_last_messages[-1].content
        if isinstance(return_value, list):
            the_text = ""
            for each in return_value:
                the_text += str(each)
            return_value = the_text

        if return_value == "":
            return_value = "No response "

        return return_value

    except Exception:
        traceback.print_exc()
