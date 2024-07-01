#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup
import platform


# Read the requirements from the requirements.txt file
with open("requirements.txt") as fp:
    install_requires = fp.read().splitlines()

if platform.system() in ["Windows"]:
    install_requires.append("AppOpener==1.7")

elif platform.system() == "Darwin": # Darwin is the system name for macOS
    install_requires.append("MacAppOpener==0.0.5") # Replace with actual macOS specific package

setup(
    name="gpt_computer_agent",
    version="1.0.0",
    description="""GPT""",
    long_description="".join(open("README.md", encoding="utf-8").readlines()),
    long_description_content_type="text/markdown",
    url="https://github.com/khulnasoft/gpt-computer-agent",
    author="KhulnaSoft DevOps",
    author_email="info@khulnasoft.com",
    license="MIT",
    packages=[
        "gpt_computer_agent",
        "gpt_computer_agent.agent",
        "gpt_computer_agent.gui",
        "gpt_computer_agent.screen",
        "gpt_computer_agent.utils",
        "gpt_computer_agent.audio",
    ],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": ["computeragent=gpt_computer_agent.start:start"],
    },
    python_requires=">= 3.9",
    zip_safe=False,
    extras_require={
        "base": install_requires,
        "default": install_requires,
        "agentic": ["crewai==0.30.11"],
        "wakeword": ["pvporcupine", "pyaudio"],
        "api": ["flask==3.0.3",],
    },
)

