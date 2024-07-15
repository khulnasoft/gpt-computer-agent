import hashlib
import sys
import threading
import base64
import time
import random
import os
import math

import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout, QShortcut, QSpacerItem, QSizePolicy, QDialog, QTextEdit
from PyQt5.QtGui import QMouseEvent, QPainter, QPen, QBrush, QIcon, QPixmap, QColor, QFontDatabase, QKeySequence
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal, QObject, pyqtSlot, QThread, QPoint, QVariantAnimation
from PyQt5 import QtWidgets, QtGui, QtCore

# Custom Imports
try:
    import sounddevice as sd
    import soundfile as sf
except OSError as e:
    print(f"PortAudio library not found: {e}")
    sys.exit(1)

from pygame import mixer

# Additional custom imports
try:
    from .agent.chat_history import *
    from .agent.agent import *
    from .llm import *
    from .llm_settings import llm_settings
    from .agent.background import *
    from .gui.signal import *
    from .gui.button import *
    from .gui.settings import settings_popup
    from .gui.llmsettings import llmsettings_popup
    from .utils.db import *
    from .utils.telemetry import my_tracer, os_name
    from .audio.wake_word import wake_word
except ImportError:
    from agent.chat_history import *
    from agent.agent import *
    from llm import *
    from llm_settings import llm_settings
    from agent.background import *
    from utils.db import *
    from gui.signal import *
    from gui.button import *
    from gui.settings import settings_popup
    from gui.llmsettings import llmsettings_popup
    from utils.telemetry import my_tracer, os_name
    from audio.wake_word import wake_word

print("Imported all libraries")

try:
    import ctypes
    myappid = "khulnasoft.gpt_computer_agent.gui.1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception as e:
    print(f"Error setting app user model ID: {e}")


# Globals
the_input_box = None
the_main_window = None
user_id = load_user_id()
os_name_ = os_name()

class Worker(QThread):
    text_to_set = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.the_input_text = None
        self.commited_text = []

    def run(self):
        while True:
            self.msleep(500)
            if self.the_input_text:
                last_text = self.commited_text[-1] if self.commited_text else ""
                if self.the_input_text != last_text:
                    self.commited_text.append(self.the_input_text)
                    if len(self.the_input_text) > 90 or MainWindow.api_enabled:
                        self.text_to_set.emit(self.the_input_text)
                    else:
                        for i in range(len(self.the_input_text)):
                            self.text_to_set.emit(self.the_input_text[:i + 1])
                            self.msleep(10)

class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            return_key_event()
        super().keyPress

class Worker2(QThread):
    text_to_set = pyqtSignal(str)
    text_to_set_title_bar = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.the_input_text = None
        self.title_bar_text = None
        self.prev = None
        self.commited_text = []

    def run(self):
        while True:
            self.msleep(500)
            if self.the_input_text and (self.prev is None or self.prev != self.the_input_text):
                self.prev = self.the_input_text
                self.text_to_set.emit("True")
                for i in range(len(self.title_bar_text)):
                    self.text_to_set_title_bar.emit(self.title_bar_text[:i + 1])
                    self.msleep(10)
