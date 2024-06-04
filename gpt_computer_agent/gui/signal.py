from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal, QObject

class SignalHandler(QObject):
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    agent_thinking = pyqtSignal()
    agent_response_ready = pyqtSignal()
    agent_response_stopped = pyqtSignal()

signal_handler = SignalHandler()
