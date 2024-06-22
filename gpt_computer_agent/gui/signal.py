from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal, QObject



class SignalHandler(QObject):
    """
    A QObject subclass to handle signals used in the GUI application.

    This class defines several signals that can be used to communicate
    between different components of the GUI application.

    Signals:
    - recording_started: Signal emitted when recording is started.
    - recording_stopped: Signal emitted when recording is stopped.
    - agent_thinking: Signal emitted when the agent is processing a request.
    - agent_response_ready: Signal emitted when the agent response is ready to be displayed.
    - agent_response_stopped: Signal emitted when the agent response display is stopped.

    """
    
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    agent_thinking = pyqtSignal()
    agent_response_ready = pyqtSignal()
    agent_response_stopped = pyqtSignal()

signal_handler = SignalHandler()

