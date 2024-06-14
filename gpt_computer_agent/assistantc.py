from .utils.db importassistants

class Assistant:
    """
    Represents an assistant within the system.

    This class defines an assistant with a specific role, goal, and backstory. Upon initialization,
    the assistant is added to the global list of assistants.

    Attributes:
    - role (str): The role of the assistant.
    - goal (str): The goal or objective of the assistant.
    - backstory (str): The backstory or history of the assistant.

    Methods:
    - __init__(role, goal, backstory): Initializes the Assistant object and adds it to the global list of assistants.

    Global Variables:
    - assistants (list): A global list containing information about all assistants in the system.
    """
    def __init__(self, role, goal, backstory):
        """
        Initializes a new Assistant object and adds it to the global list of assistants.

        Parameters:
        - role (str): The role of the assistant.
        - goal (str): The goal or objective of the assistant.
        - backstory (str): The backstory or history of the assistant.

        Returns:
        None
        """
        global assistants
        assistants.append({"role": role, "goal": goal, "backstory": backstory})
