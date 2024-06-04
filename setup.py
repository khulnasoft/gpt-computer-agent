#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup

with open('requirements.txt') as fp:
    install_requires = fp.read()
setup(
    name="gpt_computer_agent",
    version="0.1.1",
    description="""GPT""",
    long_description="".join(open("README.md", encoding="utf-8").readlines()),
    long_description_content_type="text/markdown",
    url="https://github.com/khulnasoft/gpt-computer-agent",
    author="KhulnaSoft Ltd",
    author_email="info@khulnasoft.com",
    license="MIT",
    packages=["gpt_computer_agent", "gpt_computer_agent.agent", "gpt_computer_agent.gui", "gpt_computer_agent.screen", "gpt_computer_agent.utils", "gpt_computer_agent.audio"],
    install_requires=install_requires,
    entry_points={
        "console_scripts": ["computeragent=gpt_computer_agent.start:start"],
    },      
    python_requires=">= 3.9",
    zip_safe=False,
)
