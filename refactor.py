import os
import subprocess


def install_refactor_tool():
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'ruff==0.6.0'])


def refactor():
    subprocess.check_call(['ruff', 'check', '--fix'])
    subprocess.check_call(['ruff', 'format'])


def create_commit(version):
    subprocess.check_call(['git', 'add', '.'])
    subprocess.check_call(['git', 'commit', '-m', f'refactor: Scheduled refactoring {version}'])


def push():
    subprocess.check_call(['git', 'push'])


if __name__ == "__main__":
    install_refactor_tool()
    refactor()
    create_commit('0.28.3')
    push()
