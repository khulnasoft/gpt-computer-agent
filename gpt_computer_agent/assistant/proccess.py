try:
    from ..llm import *
    from .agent import *
    from .chat_history import *
    from ..audio.tts import text_to_speech
    from ..audio.stt import speech_to_text
    from ..audio.record import audio_data
    from ..gui.signal import signal_handler
    from ..utils.db import *
    from ..utils.telemetry import my_tracer, os_name
except ImportError:
    from llm import *
    from assistant.agent import *
    from assistant.chat_history import *
    from audio.tts import text_to_speech
    from audio.stt import speech_to_text
    from audio.record import audio_data
    from gui.signal import signal_handler
    from utils.db import *
    from utils.telemetry import my_tracer, os_name


import threading
import traceback


from pygame import mixer


import time
import random

last_ai_response = None
user_id = load_user_id()
os_name_ = os_name()


def process_audio(take_screenshot=True, take_system_audio=False, dont_save_image=False):
    with my_tracer.start_span("process_audio") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("os_name", os_name_)
        try:
            global audio_data, last_ai_response
            from ..gpt_computer_agent import the_input_box, the_main_window
            from ..audio.record import audio_data, the_input_box_pre


            transcription = speech_to_text(mic_record_location)

            if take_system_audio:

                transcription2 = speech_to_text(system_sound_location)

            llm_input = transcription

            print("LLM INPUT (screenshot)", the_input_box_pre)
            if (
                        the_input_box_pre != ""
                        and the_input_box_pre != "Thinking..."
                        and the_input_box_pre != last_ai_response
                    ):
                llm_input += the_input_box_pre

            if take_system_audio:
                llm_input += " \n Other of USER: " + transcription2

            llm_output = agent(
                llm_input,
                get_chat_message_history().messages,
                get_client(),
                screenshot_path=screenshot_path if take_screenshot else None,
                dont_save_image=dont_save_image,
            )
            last_ai_response = llm_output

            if not is_just_text_model_active():
                response_path = text_to_speech(llm_output)
                signal_handler.agent_response_ready.emit()

                def play_text():
                    from ..gpt_computer_agent import the_input_box, the_main_window

                    global last_ai_response
                    if (
                        the_input_box.toPlainText() == ""
                        or the_input_box.toPlainText() == "Thinking..."
                        or the_input_box.toPlainText() == last_ai_response
                    ):
                        the_main_window.update_from_thread(llm_output)
   

                def play_audio():
                    from ..gpt_computer_agent import the_input_box, the_main_window
                    with my_tracer.start_span("play_audio") as span:
                        span.set_attribute("user_id", user_id)
                        span.set_attribute("os_name", os_name_)
                        play_text()
                        mixer.init()
                        mixer.music.load(response_path)
                        mixer.music.play()
                        while mixer.music.get_busy():
                            if the_main_window.stop_talking:
                                mixer.music.stop()
                                the_main_window.stop_talking = False
                                break
                            time.sleep(0.1)
                        signal_handler.agent_response_stopped.emit()

                playback_thread = threading.Thread(target=play_audio)
                playback_thread.start()
            else:
                signal_handler.agent_response_ready.emit()

                def play_text():
                    from ..gpt_computer_agent import the_input_box, the_main_window
            
                    the_main_window.update_from_thread(llm_output)
                    signal_handler.agent_response_stopped.emit()

                playback_thread = threading.Thread(target=play_text)
                playback_thread.start()
        except Exception as e:
            print("Error in process_audio", e)
            traceback.print_exc()
            from ..gpt_computer_agent import the_input_box, the_main_window
            the_main_window.update_from_thread("EXCEPTION: " + str(e))
            signal_handler.agent_response_stopped.emit()


def process_screenshot():
    with my_tracer.start_span("process_screenshot") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("os_name", os_name_)
        try:


            global last_ai_response
            from ..gpt_computer_agent import the_input_box, the_main_window
            from ..audio.record import audio_data, the_input_box_pre

            llm_input =  "I just take a screenshot. for you to remember. Just say ok."
            

            if (
                        the_input_box_pre != ""
                        and the_input_box_pre != "Thinking..."
                        and the_input_box_pre != last_ai_response
                    ):
                llm_input += the_input_box_pre

            print("LLM INPUT (just screenshot)", llm_input)



            llm_output = agent(
                llm_input,
                get_chat_message_history().messages,
                get_client(),
                screenshot_path=just_screenshot_path,
                dont_save_image=True,
            )
            last_ai_response = llm_output

            if not is_just_text_model_active():
                response_path = text_to_speech(llm_output)
                signal_handler.agent_response_ready.emit()

                def play_text():
                    from ..gpt_computer_agent import the_input_box, the_main_window

                    global last_ai_response
                    if (
                        the_input_box.toPlainText() == ""
                        or the_input_box.toPlainText() == "Thinking..."
                        or the_input_box.toPlainText() == last_ai_response
                    ):
                        the_main_window.update_from_thread(llm_output)
                        

                def play_audio():
                    from ..gpt_computer_agent import the_input_box, the_main_window
                    with my_tracer.start_span("play_audio") as span:
                        span.set_attribute("user_id", user_id)
                        span.set_attribute("os_name", os_name_)
                        play_text()
                        mixer.init()
                        mixer.music.load(response_path)
                        mixer.music.play()
                        while mixer.music.get_busy():
                            if the_main_window.stop_talking:
                                mixer.music.stop()
                                the_main_window.stop_talking = False
                                break
                            time.sleep(0.1)
                        signal_handler.agent_response_stopped.emit()

                playback_thread = threading.Thread(target=play_audio)
                playback_thread.start()
            else:
                signal_handler.agent_response_ready.emit()

                def play_text():
                    from ..gpt_computer_agent import the_input_box, the_main_window


                    the_main_window.update_from_thread(llm_output)
                    signal_handler.agent_response_stopped.emit()

                playback_thread = threading.Thread(target=play_text)
                playback_thread.start()


        except Exception as e:
            print("Error in process_screenshot", e)
            traceback.print_exc()
            from ..gpt_computer_agent import the_input_box, the_main_window
            the_main_window.update_from_thread("EXCEPTION: " + str(e))
            signal_handler.agent_response_stopped.emit()



def process_text(text, screenshot_path=None):
    with my_tracer.start_span("process_text") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("os_name", os_name_)
        try:

            global last_ai_response

            llm_input = text

            llm_output = agent(
                llm_input,
                get_chat_message_history().messages,
                get_client(),
                screenshot_path=screenshot_path,
                dont_save_image=True,
            )
            last_ai_response = llm_output

            if not is_just_text_model_active():

                def play_text():
                    from ..gpt_computer_agent import the_input_box, the_main_window
                    global last_ai_response
                    
                    if (
                        the_input_box.toPlainText() == ""
                        or the_input_box.toPlainText() == "Thinking..."
                        or the_input_box.toPlainText() == last_ai_response
                    ):

                        the_main_window.update_from_thread(llm_output)
                        

                if load_api_key() != "CHANGE_ME":
                    response_path = text_to_speech(llm_output)
                    signal_handler.agent_response_ready.emit()

                    def play_audio():
                        from ..gpt_computer_agent import the_input_box, the_main_window
                        with my_tracer.start_span("play_audio") as span:
                            span.set_attribute("user_id", user_id)
                            span.set_attribute("os_name", os_name_)
                            play_text()
                            mixer.init()
                            mixer.music.load(response_path)
                            mixer.music.play()
                            while mixer.music.get_busy():
                                if the_main_window.stop_talking:
                                    mixer.music.stop()
                                    the_main_window.stop_talking = False
                                    break
                                time.sleep(0.1)
                            signal_handler.agent_response_stopped.emit()

                    playback_thread = threading.Thread(target=play_audio)
                    playback_thread.start()
                else:
                    signal_handler.agent_response_ready.emit()
                    play_text()
                    signal_handler.agent_response_stopped.emit()

            else:
                signal_handler.agent_response_ready.emit()

                def play_text():
                    from ..gpt_computer_agent import the_input_box, the_main_window


                    the_main_window.update_from_thread(llm_output)
                    signal_handler.agent_response_stopped.emit()

                playback_thread = threading.Thread(target=play_text)
                playback_thread.start()


        except Exception as e:
            print("Error in process_text", e)
            traceback.print_exc()
            from ..gpt_computer_agent import the_input_box, the_main_window
            the_main_window.update_from_thread("EXCEPTION: " + str(e))
            signal_handler.agent_response_stopped.emit()
