# Create a python api and start_api function via flask

from flask import Flask, request, jsonify
import threading
import time
import pyautogui
from werkzeug.serving import make_server

from waitress import serve

app = Flask(__name__)


@app.route("/status", methods=["POST"])
def status():
    return jsonify({"response": True})


def the_input(text, screen, talk):
    print("Input:", text)

    from .agent.process import process_text_api
    from .utils.db import (
        screenshot_path,
    )

    if screen != "true":
        result = process_text_api(text, None)
    else:
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        result = process_text_api(text, screenshot_path)

    return jsonify({"response": result})


@app.route("/input", methods=["POST"])
def input():
    """
    This function receives input from the user and returns the response.
    """
    data = request.json
    text = data["text"]
    screen = data["screen"]
    talk = data["talk"]

    return the_input(text, screen, talk)


@app.route("/request", methods=["POST"])
def the_request():
    """
    This function receives input from the user and returns the response.
    """
    data = request.json
    the_request = data["request"]
    the_response = data["response"]
    if "screen" in data:
        screen = data["screen"]
    else:
        screen = "false"

    combined = the_request + "\n" + the_response

    return the_input(combined, screen, "false")


@app.route("/screenshot", methods=["POST"])
def screenshot():
    """
    This function receives a screenshot from the user and returns the response.
    """
    from .gpt_computer_agent import the_main_window, the_input_box

    firsst_text = the_input_box.toPlainText()
    the_main_window.button_handler.just_screenshot()

    while the_input_box.toPlainText() == firsst_text:
        time.sleep(0.3)

    while the_input_box.toPlainText().startswith("System:"):
        time.sleep(0.3)

    while not the_main_window.state == "idle":
        time.sleep(0.3)

    response = the_input_box.toPlainText()

    return jsonify({"response": response})


@app.route("/tts", methods=["POST"])
def tts():
    """
    This function receives a text to speech request from the user and returns the response.
    """
    from .gpt_computer_agent import the_main_window

    original_tts = the_main_window.tts_available
    the_main_window.tts_available = True
    the_main_window.manuel_stop = True
    data = request.json
    text = data["text"]
    print("TTS:", text)
    from .agent.process import tts_if_you_can

    tts_if_you_can(
        text, not_threaded=False, status_edit=True, bypass_other_settings=True
    )
    the_main_window.tts_available = original_tts

    return jsonify({"response": "TTS request received"})


@app.route("/profile", methods=["POST"])
def profile():
    """
    This function sets the profile for the application.
    """
    data = request.json
    profile = data["profile"]
    print("Profile:", profile)
    from .utils.db import set_profile

    set_profile(profile)

    return jsonify({"response": "Profile set to " + profile})


@app.route("/reset_memory", methods=["POST"])
def reset_memory():
    """
    This function resets the memory of the application.
    """
    from .agent.chat_history import clear_chat_history

    clear_chat_history()

    return jsonify({"response": "Memory reset"})


@app.route("/activate_predefined_agents", methods=["POST"])
def enable_predefined_agents():
    """
    This function enables predefined agents for the application.
    """
    from .utils.db import activate_predefined_agents_setting

    activate_predefined_agents_setting()

    return jsonify({"response": "Predefined agents enabled"})


@app.route("/deactivate_predefined_agents", methods=["POST"])
def disable_predefined_agents():
    """
    This function disables predefined agents for the application.
    """
    from .utils.db import deactivate_predefined_agents_setting

    deactivate_predefined_agents_setting()

    return jsonify({"response": "Predefined agents disabled"})


@app.route("/activate_online_tools", methods=["POST"])
def enable_online_tools():
    """
    This function enables online tools for the application.
    """
    from .utils.db import activate_online_tools_setting

    activate_online_tools_setting()

    return jsonify({"response": "Online tools enabled"})


@app.route("/deactivate_online_tools", methods=["POST"])
def disable_online_tools():
    """
    This function disables online tools for the application.
    """
    from .utils.db import deactivate_online_tools_setting

    deactivate_online_tools_setting()

    return jsonify({"response": "Online tools disabled"})


@app.route("/change_name", methods=["POST"])
def change_name():
    """
    This function changes the name of the application.
    """
    data = request.json
    new_name = data["new_name"]
    print("Name:", new_name)
    from .character import change_name

    change_name(new_name)
    return jsonify({"response": "Name changed to " + new_name})


@app.route("/change_developer", methods=["POST"])
def change_developer():
    """
    This function changes the developer of the application.
    """
    data = request.json
    new_developer = data["new_developer"]
    print("Developer:", new_developer)
    from .character import change_developer

    change_developer(new_developer)
    return jsonify({"response": "Developer changed to " + new_developer})


@app.route("/library_install", methods=["POST"])
def library_install():
    """
    This function install a library.
    """
    data = request.json
    library = data["library"]
    print("Library İnstall:", library)
    from .utils.pypi import install_library

    if install_library(library):
        return jsonify({"response": f"Library {library} installed"})
    else:
        return jsonify({"response": f"Library {library} installation failed"})


@app.route("/library_uninstall", methods=["POST"])
def library_uninstall():
    """
    This function uninstall a library.
    """
    data = request.json
    library = data["library"]
    print("Library Uninstall:", library)
    from .utils.pypi import uninstall_library

    if uninstall_library(library):
        return jsonify({"response": f"Library {library} uninstalled"})
    else:
        return jsonify({"response": f"Library {library} uninstallation failed"})


@app.route("/custom_tool", methods=["POST"])
def custom_tool():
    """
    This function adds a custom tool to the application.
    """
    data = request.json
    code = data["code"]
    print("Custom Tool:", code)
    from .utils.function import string_to_function

    try:
        func = string_to_function(code)
        from .tooler import Tool

        Tool(func)
        return jsonify({"response": f"Custom tool {func.__name__} added"})
    except Exception as e:
        return jsonify({"response": f"Custom tool addition failed: {e}"}), 500


@app.route("/top_bar_activate", methods=["POST"])
def top_bar_activate():
    """
    This function serve an animation of top bar to show an operations especialy
    """
    from .gpt_computer_agent import the_main_window

    data = request.json
    text = data["text"]

    the_main_window.active_border_animation(text)
    return jsonify({"response": "Activated top bar animation"})


@app.route("/top_bar_deactivate", methods=["POST"])
def top_bar_deactivate():
    """
    This function stop the top bar animation
    """
    from .gpt_computer_agent import the_main_window

    data = request.json
    text = data["text"]
    the_main_window.deactive_border_animation(text)
    return jsonify({"response": "Deactivated top bar animation"})


@app.route("/boop_sound", methods=["POST"])
def boop_sound():
    """
    This function sound an boop to user
    """

    from .gpt_computer_agent import click_sound

    click_sound()
    return jsonify({"response": "Sound played"})


@app.route("/ask_to_user", methods=["POST"])
def ask_to_user():
    """
    This api asks question to the user and return the result
    """
    data = request.json
    question = data["question"]
    wait_for_answer = data["wait_for_answer"]
    from .standard_tools import ask_to_user

    result = ask_to_user(question, wait_for_answer)
    return jsonify({"response": result})


@app.route("/set_text", methods=["POST"])
def set_text():
    """
    This api set text to main window text input
    """
    data = request.json
    text = data["text"]
    from .gpt_computer_agent import the_main_window

    the_main_window.set_text_from_api(text)
    return jsonify({"response": "Text set."})


@app.route("/set_background_color", methods=["POST"])
def set_background_color():
    """
    This api set text to main window text input
    """
    data = request.json
    color = data["color"]
    from .gpt_computer_agent import the_main_window

    the_main_window.set_background_color(color)
    return jsonify({"response": "Background color set."})


@app.route("/set_opacity", methods=["POST"])
def set_opacity():
    """
    This api set text to main window text input
    """
    data = request.json
    opacity = data["opacity"]
    from .gpt_computer_agent import the_main_window

    the_main_window.set_opacity(opacity)
    return jsonify({"response": "Opacity set."})


@app.route("/set_border_radius", methods=["POST"])
def set_border_radius():
    """
    This api set text to main window text input
    """
    data = request.json
    radius = data["radius"]
    from .gpt_computer_agent import the_main_window

    the_main_window.set_border_radius(radius)
    return jsonify({"response": "Border radius set."})


@app.route("/collapse", methods=["POST"])
def collapse():
    """
    This api set text to main window text input
    """
    from .gpt_computer_agent import the_main_window

    the_main_window.collapse_gca_api()
    return jsonify({"response": "Collapsed."})


@app.route("/expand", methods=["POST"])
def expand():
    """
    This api set text to main window text input
    """
    from .gpt_computer_agent import the_main_window

    the_main_window.uncollapse_gca_api()
    return jsonify({"response": "Expanded."})


@app.route("/save_openai_api_key", methods=["POST"])
def save_openai_api_key():
    """
    This api saves the OpenAI API key
    """
    data = request.json
    openai_api_key = data["openai_api_key"]
    from .utils.db import save_api_key

    save_api_key(openai_api_key)
    return jsonify({"response": "OpenAI API key saved."})


@app.route("/save_user_id", methods=["POST"])
def save_user_id():
    """
    This api saves the user id
    """
    data = request.json
    user_id = data["user_id"]
    from .utils.db import change_user_id

    change_user_id(user_id)
    return jsonify({"response": "User id changed."})


@app.route("/save_aws_access_key_id", methods=["POST"])
def save_aws_access_key_id():
    data = request.json
    aws_access_key_id = data["aws_access_key_id"]
    from .utils.db import save_aws_access_key_id

    save_aws_access_key_id(aws_access_key_id)
    return jsonify({"response": "aws_access_key_id key saved."})


@app.route("/save_aws_secret_access_key", methods=["POST"])
def save_aws_secret_access_key():
    data = request.json
    aws_secret_access_key = data["aws_secret_access_key"]
    from .utils.db import save_aws_secret_access_key

    save_aws_secret_access_key(aws_secret_access_key)
    return jsonify({"response": "aws_secret_access_key key saved."})


@app.route("/save_system_prompt", methods=["POST"])
def save_system_prompt():
    """
    This api saves the prompt
    """
    data = request.json
    prompt = data["prompt"]
    from .utils.db import save_system_prompt

    save_system_prompt(prompt)
    return jsonify({"response": "prompt saved."})


@app.route("/save_anthropic_api_key", methods=["POST"])
def save_anthropic_api_key():
    """
    This api saves the
    """
    data = request.json
    anthropic_api_key = data["anthropic_api_key"]
    from .utils.db import save_anthropic_api_key

    save_anthropic_api_key(anthropic_api_key)
    return jsonify({"response": "Anthropic API key saved."})


@app.route("/save_openai_url", methods=["POST"])
def save_openai_url():
    """
    This api saves the OpenAI base URL
    """
    data = request.json
    openai_url = data["openai_url"]
    from .utils.db import save_openai_url

    save_openai_url(openai_url)
    return jsonify({"response": "OpenAI base URL saved."})


@app.route("/save_api_version", methods=["POST"])
def save_api_version():
    """
    This api saves the OpenAI base URL
    """
    data = request.json
    api_version = data["api_version"]
    from .utils.db import save_api_version

    save_api_version(api_version)
    return jsonify({"response": "API version saved."})


@app.route("/save_model_settings", methods=["POST"])
def save_model_settings():
    """
    This api saves the model settings
    """
    data = request.json
    model_settings = data["model_settings"]
    from .utils.db import save_model_settings

    save_model_settings(model_settings)
    return jsonify({"response": "Model settings saved."})


@app.route("/save_groq_api_key", methods=["POST"])
def save_groq_api_key():
    """
    This api saves the Groq API key
    """
    data = request.json
    groq_api_key = data["groq_api_key"]
    from .utils.db import save_groq_api_key

    save_groq_api_key(groq_api_key)
    return jsonify({"response": "Groq API key saved."})


@app.route("/save_google_api_key", methods=["POST"])
def save_google_api_key():
    """
    This api saves the Google Generative AI API key
    """
    data = request.json
    google_api_key = data["google_api_key"]
    from .utils.db import save_google_api_key

    save_google_api_key(google_api_key)
    return jsonify({"response": "Google Generative AI API key saved."})


@app.route("/save_tts_model_settings", methods=["POST"])
def save_tts_model_settings():
    """
    This api saves the TTS model settings
    """
    data = request.json
    tts_model_settings = data["tts_model_settings"]
    from .utils.db import save_tts_model_settings

    save_tts_model_settings(tts_model_settings)
    return jsonify({"response": "TTS model settings saved."})


@app.route("/save_stt_model_settings", methods=["POST"])
def save_stt_model_settings():
    """
    This api saves the STT model settings
    """
    data = request.json
    stt_model_settings = data["stt_model_settings"]
    from .utils.db import save_stt_model_settings

    save_stt_model_settings(stt_model_settings)
    return jsonify({"response": "STT model settings saved."})


@app.route("/show_logo", methods=["POST"])
def show_logo():
    """
    This api shows the custom logo
    """
    from .utils.db import activate_logo_active_setting

    activate_logo_active_setting()
    from .gpt_computer_agent import the_main_window

    the_main_window.show_logo_api()
    return jsonify({"response": "Custom logo activated."})


@app.route("/hide_logo", methods=["POST"])
def hide_logo():
    """
    This api hides the custom logo
    """
    from .utils.db import deactivate_logo_active_setting

    deactivate_logo_active_setting()
    from .gpt_computer_agent import the_main_window

    the_main_window.hide_logo_api()
    return jsonify({"response": "Custom logo deactivated."})


@app.route("/default_logo", methods=["POST"])
def default_logo():
    """
    This api enable default logo
    """
    from .utils.db import (
        save_logo_file_path,
        icon_256_path,
        is_logo_active_setting_active,
    )

    save_logo_file_path(icon_256_path)

    from .gpt_computer_agent import the_main_window

    the_main_window.tray_and_task_bar_logo_api()
    if is_logo_active_setting_active():
        the_main_window.show_logo_api()
    return jsonify({"response": "Custom logo deactivated."})


@app.route("/custom_logo_upload", methods=["POST"])
def custom_logo_upload():
    """
    This api uploads a custom logo
    """
    file = request.files["logo"]
    from .utils.db import (
        save_logo_file_path,
        custom_logo_path,
        is_logo_active_setting_active,
    )

    file.save(custom_logo_path)
    save_logo_file_path(custom_logo_path)
    from .gpt_computer_agent import the_main_window

    the_main_window.tray_and_task_bar_logo_api()
    if is_logo_active_setting_active():
        the_main_window.show_logo_api()
    return jsonify({"response": "Custom logo uploaded."})


@app.route("/activate_long_gca", methods=["POST"])
def activate_long_gca():
    """
    This api activates long GCA
    """
    from .gpt_computer_agent import the_main_window

    the_main_window.activate_long_gca_api()
    return jsonify({"response": "Long GCA activated."})


@app.route("/deactivate_long_gca", methods=["POST"])
def deactivate_long_gca():
    """
    This api deactivates long GCA
    """
    from .gpt_computer_agent import the_main_window

    the_main_window.deactivate_long_gca_api()
    return jsonify({"response": "Long GCA deactivated."})


@app.route("/train", methods=["POST"])
def train():
    """
    This api trains the gca with given url
    """
    data = request.json
    url = data["url"]
    from .utils.train import train

    the_result = train(url)
    return jsonify({"response": the_result})


@app.route("/get_openai_models", methods=["POST"])
def get_openai_models():
    """
    This api returns the list of OpenAI models
    """
    from .llm_settings import get_openai_models

    return jsonify({"response": get_openai_models()})


@app.route("/get_azureai_models", methods=["POST"])
def get_azureai_models():
    """
    This api returns the list of Azure AI models
    """
    from .llm_settings import get_azureai_models

    return jsonify({"response": get_azureai_models()})


@app.route("/get_ollama_models", methods=["POST"])
def get_ollama_models():
    """
    This api returns the list of Ollama models
    """
    from .llm_settings import get_ollama_models

    return jsonify({"response": get_ollama_models()})


@app.route("/get_google_models", methods=["POST"])
def get_google_models():
    """
    This api returns the list of Google models
    """
    from .llm_settings import get_google_models

    return jsonify({"response": get_google_models()})


@app.route("/get_groq_models", methods=["POST"])
def get_groq_models():
    """
    This api returns the list of Groq models
    """
    from .llm_settings import get_groq_models

    return jsonify({"response": get_groq_models()})


@app.route("/mouse_scroll_down", methods=["POST"])
def mouse_scroll_down():
    data = request.json
    amount = data["amount"]

    from .display_tools import mouse_scroll_

    mouse_scroll_("down", amount)
    return jsonify({"response": f"Mouse scrolled down by {amount}"})


@app.route("/mouse_scroll_up", methods=["POST"])
def mouse_scroll_up():
    data = request.json
    amount = data["amount"]

    from .display_tools import mouse_scroll_

    mouse_scroll_("up", amount)
    return jsonify({"response": f"Mouse scrolled up by {amount}"})


@app.route("/add_mcp", methods=["POST"])
def add_mcp():
    data = request.json
    name = data["name"]
    command = data["command"]
    args = data["args"]
    from .mcp.tool import add_custom_mcp_server

    add_custom_mcp_server(name, command, args)
    return jsonify({"response": "MCP added."})


@app.route("/stop_server", methods=["POST"])
def stop_server():
    try:
        try:
            from .gpt_computer_agent import the_main_window

            the_main_window.close()
        except ImportError:
            from gpt_computer_agent.gpt_computer_agent import the_main_window

            the_main_window.close()
    except:
        pass

    stop_api()
    exit(0)


class ServerThread(threading.Thread):
    def __init__(self, app, host, port):
        threading.Thread.__init__(self)
        self.srv = make_server(host, port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print("Starting server")
        self.srv.serve_forever()

    def shutdown(self):
        print("Stopping server")
        self.srv.shutdown()


server_thread = None


def start_api(api=False):
    if api == False:
        global server_thread
        if server_thread is None:
            server_thread = ServerThread(app, "0.0.0.0", 7541)
            server_thread.start()
            print("API started")
        else:
            print("API is already running")

    else:
        serve(app, host="0.0.0.0", port=7541)


def stop_api():
    global server_thread
    if server_thread is not None:
        server_thread.shutdown()
        server_thread.join()
        server_thread = None
        print("API stopped")
    else:
        print("API is not running")
