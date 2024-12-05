#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import platform

# Read the requirements from the requirements.txt file
with open("requirements.txt") as fp:
    base_requirements = fp.read().splitlines()

# Platform-specific dependencies
if platform.system() == "Windows":
    base_requirements.append("AppOpener==1.7")

elif platform.system() == "Darwin":  # Darwin is the system name for macOS
    base_requirements.append("MacAppOpener==0.0.5")

# Optional dependencies
extras_require = {
    "agentic": ["crewai==0.86.0"],
    "wakeword": ["pvporcupine", "pyaudio"],
    "api": ["flask==3.0.3"],
    "local_tts": [
        "tensorflow==2.17.0",
        "datasets[audio]==2.20.0",
        "sentencepiece==0.2.0",
        "torch==2.4.0",
        "transformers==4.43.3",
    ],
    "local_stt": ["openai-whisper==20231117"],
}

# Merge base requirements with extras
extras_require["default"] = base_requirements
extras_require["base"] = base_requirements

setup(
    name="gpt_computer_agent",
    version="0.22.4",
    description="GPT Computer Agent - A multi-purpose agent system",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/khulnasoft/gpt-computer-agent",
    author="KhulnaSoft DevOps",
    author_email="info@khulnasoft.com",
    license="MIT",
    packages=find_packages(include=[
        "client",
        "client.*",
        "server",
        "server.*",
        "shared",
        "shared.*"
    ]),
    include_package_data=True,
    install_requires=base_requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": ["computeragent=client.agent:start"],  # Adjusted for new structure
    },
    python_requires=">=3.9",
    zip_safe=False,
)
