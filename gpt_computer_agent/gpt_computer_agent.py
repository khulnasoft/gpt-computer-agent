from .agent.chat_history import *
from .agent.agent import *
from .llm import *
from .agent.background import *

from .gui.signal import *
from .gui.button import *

from .utils.db import *

import hashlib
import sys
import threading
import base64
import time
import random
import numpy as np
import sounddevice as sd
import soundfile as sf
from .utils.db import load_api_key

from pygame import mixer
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QMouseEvent, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal, QObject
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut
import os
import scipy.io.wavfile as wavfile

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, QPoint

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon


print("Imported all libraries")


from PyQt5 import QtCore


try:
    import ctypes

    myappid = "khulnasoft.gpt_computer_agent.gui.1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

the_input_box = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.state = "idle"
        self.pulse_timer = None

        self.button_handler = ButtonHandler(self)
        self.initUI()
        self.old_position = self.pos()

    def initUI(self):
        self.setWindowTitle("GPT")
        self.setGeometry(100, 100, 200, 200)

        app_icon = QtGui.QIcon()
        app_icon.addFile(icon_16_path, QtCore.QSize(16, 16))
        app_icon.addFile(icon_24_path, QtCore.QSize(24, 24))
        app_icon.addFile(icon_32_path, QtCore.QSize(32, 32))
        app_icon.addFile(icon_48_path, QtCore.QSize(48, 48))
        app_icon.addFile(icon_256_path, QtCore.QSize(256, 256))
        self.setWindowIcon(app_icon)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Custom title bar
        self.title_bar = QWidget(self)
        self.title_bar.setFixedHeight(20)  # Set a fixed height for the title bar
        self.title_bar_layout = QHBoxLayout(self.title_bar)
        self.title_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.title_bar_layout.setSpacing(0)

        layout.addWidget(self.title_bar)

        # Add other UI elements below the title bar
        self.other_widget = QWidget(self)
        layout.addWidget(self.other_widget)

        self.layout = layout

        self.setLayout(layout)

        # Add keyboard shortcuts
        self.shortcut_screenshot = QShortcut(QKeySequence("Ctrl+1"), self)
        self.shortcut_screenshot.activated.connect(
            lambda: self.button_handler.just_screenshot()
        )
        self.shortcut_screenshot = QShortcut(QKeySequence("Ctrl+2"), self)
        self.shortcut_screenshot.activated.connect(
            lambda: self.button_handler.toggle_recording(take_system_audio=True)
        )

        self.shortcut_no_screenshot = QShortcut(QKeySequence("Ctrl+e"), self)
        self.shortcut_no_screenshot.activated.connect(
            lambda: self.button_handler.toggle_recording(take_system_audio=True)
        )

        self.shortcut_no_screenshot = QShortcut(QKeySequence("Ctrl+3"), self)
        self.shortcut_no_screenshot.activated.connect(
            lambda: self.button_handler.toggle_recording(no_screenshot=True)
        )

        # I want to create an input box to bottom left and a send button to bottom right

        input_box = QLineEdit(self)

        if load_api_key() == "CHANGE_ME":
            input_box.setPlaceholderText("Save your API Key, go to settings")
        else:
            input_box.setPlaceholderText("Type here")
        input_box.setGeometry(30, self.height() - 60, 200, 30)
        global the_input_box
        the_input_box = input_box

        def input_box_send():
            if input_box.text() != "":
                self.button_handler.input_text(input_box.text())
                input_box.setText("")

        def input_box_send_screenshot():
            if input_box.text() != "":
                self.button_handler.input_text_screenshot(input_box.text())
                input_box.setText("")

        self.layout.addWidget(input_box)

        # Create a horizontal layout
        button_layout = QHBoxLayout()

        # Create the send button
        send_button = QPushButton("Send", self)
        send_button.clicked.connect(input_box_send)

        # Create the screenshot button
        screenshot_button = QPushButton("+Screenshot", self)
        screenshot_button.clicked.connect(input_box_send_screenshot)

        # Add the buttons to the horizontal layout
        button_layout.addWidget(send_button)
        button_layout.addWidget(screenshot_button)

        self.shortcut_enter = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.shortcut_enter.activated.connect(input_box_send_screenshot)
        self.shortcut_enter = QShortcut(QKeySequence("Return"), self)
        self.shortcut_enter.activated.connect(input_box_send)

        self.layout.addLayout(button_layout)

        settingsButton = QPushButton("Settings", self)

        settingsButton.clicked.connect(self.button_handler.settings_popup)
        button_layout_ = QHBoxLayout()
        button_layout_.addWidget(settingsButton)
        self.layout.addLayout(button_layout_)

        self.show()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.old_position = event.globalPos()

    def mouseMoveEvent(self, event: QMouseEvent):
        delta = QPoint(event.globalPos() - self.old_position)
        if event.buttons() == Qt.LeftButton and self.title_bar.underMouse():
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_position = event.globalPos()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 8, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))

        center_x = 100
        center_y = 50

        if self.state == "talking":
            # Draw a pulsating circle with smooth easing animation
            radius_variation = 5 * (1 + math.sin(self.pulse_frame * math.pi / 100))
            radius = 70 + radius_variation
            painter.drawEllipse(
                int(center_x - radius / 2),
                int(center_y - radius / 2),
                int(radius),
                int(radius),
            )
        elif self.state == "thinking":
            the_input_box.setText("Thinking...")
            # more slow pulsating circle with smooth easing animation
            radius_variation = 5 * (1 + math.sin(self.pulse_frame * math.pi / 100))
            radius = 70 + radius_variation
            painter.drawEllipse(
                int(center_x - radius / 2),
                int(center_y - radius / 2),
                int(radius),
                int(radius),
            )

        else:
            radius = 70
            painter.drawEllipse(
                int(center_x - radius / 2),
                int(center_y - radius / 2),
                int(radius),
                int(radius),
            )

        self.circle_rect = QRect(
            int(center_x - radius / 2),
            int(center_y - radius / 2),
            int(radius),
            int(radius),
        )

        small_center_x = self.width() - 30
        small_center_y = self.height() - 160
        small_radius = 20
        painter.drawEllipse(
            int(small_center_x - small_radius / 2),
            int(small_center_y - small_radius / 2),
            int(small_radius),
            int(small_radius),
        )

        self.small_circle_rect = QRect(
            int(small_center_x - small_radius / 2),
            int(small_center_y - small_radius / 2),
            int(small_radius),
            int(small_radius),
        )

        small_center_x = 30
        small_center_y = self.height() - 130
        small_radius = 20
        painter.drawEllipse(
            int(small_center_x - small_radius / 2),
            int(small_center_y - small_radius / 2),
            int(small_radius),
            int(small_radius),
        )

        self.small_circle_left = QRect(
            int(small_center_x - small_radius / 2),
            int(small_center_y - small_radius / 2),
            int(small_radius),
            int(small_radius),
        )

        small_center_x = 30
        small_center_y = 30
        small_radius = 25
        painter.drawEllipse(
            int(small_center_x - small_radius / 2),
            int(small_center_y - small_radius / 2),
            int(small_radius),
            int(small_radius),
        )

        self.small_circle_left_top = QRect(
            int(small_center_x - small_radius / 2),
            int(small_center_y - small_radius / 2),
            int(small_radius),
            int(small_radius),
        )

    def update_state(self, new_state):
        self.state = new_state
        print(f"State updated: {new_state}")
        if new_state == "talking":
            self.pulse_frame = 0
            if self.pulse_timer:
                self.pulse_timer.stop()
                self.pulse_timer = None
            self.pulse_timer = QTimer(self)
            self.pulse_timer.timeout.connect(self.pulse_circle)
            self.pulse_timer.start(5)
        elif new_state == "thinking":
            self.pulse_frame = 0
            if self.pulse_timer:
                self.pulse_timer.stop()
                self.pulse_timer = None
            self.pulse_timer = QTimer(self)
            self.pulse_timer.timeout.connect(self.pulse_circle)
            self.pulse_timer.start(20)
        elif self.pulse_timer:
            self.pulse_timer.stop()
            self.pulse_timer = None
        self.update()  # Trigger a repaint

    def pulse_circle(self):
        self.pulse_frame += 1
        if self.pulse_frame >= 100:
            self.pulse_frame = 0
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if self.state == "idle" or self.state == "talking":
            if self.circle_rect.contains(event.pos()):
                self.button_handler.toggle_recording(dont_save_image=True)
            elif self.small_circle_rect.contains(event.pos()):
                self.button_handler.toggle_recording(no_screenshot=True)
            elif self.small_circle_left.contains(event.pos()):
                self.button_handler.toggle_recording(take_system_audio=True)
            elif self.small_circle_left_top.contains(event.pos()):
                self.button_handler.just_screenshot()
