from cx_Freeze import setup, Excutable

import sys
sys.setrecursionlimit(10000)

setup(
    name="GPT_Computer_Agent",
    version="0.1",
    description="",
    excutables=[Excutable("run.py")])
