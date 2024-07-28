name_ = "GPT Computer Agent"
def name():
    global name_
    return name_

def change_name(new_name):
    global name_
    name_ = new_name

    from .gpt_computer_agent import the_main_window
    the_main_window.title_label.setText(name_)



developer_ = "Open Source Community"
def developer():
    global developer_
    return developer_


def change_developer(new_developer):
    global developer_
    developer_ = new_developer
