#!/usr/bin/python3

from __future__ import print_function

import os
import sys
import argparse
import platform
import subprocess

try:
    import pip
except ImportError:
    pip = None

LIB_DIR = "lib"
sys.path.insert(0, LIB_DIR)
INTERACTIVE_MODE = not len(sys.argv) > 1
PYTHON_OK = sys.version_info >= (3, 5)
IS_WINDOWS = os.name == "nt"
IS_MAC = sys.platform == "darwin"
IS_64BIT = platform.machine().endswith("64")

INTRO = ("\033[37;1m====================\033[0m\n"
         "\033[36;4m[VectorBot] Launcher\033[0m\n"
         "\033[37;1m====================\033[0m\n")

def parse_cli_args():
    parser = argparse.ArgumentParser(description="[VectorBot] Launcher")
    parser.add_argument("--start", "-s", help="Start VectorBot", action="store_true")
    parser.add_argument("--auto-restart", help="Automatically restart VectorBot", action="store_true")
    parser.add_argument("--update", "-u", help="Update Bot", action="store_true")
    parser.add_argument("--update-reqs", help="Update PIP requirements", action="store_true")
    parser.add_argument("--reset", help="Reset Bot (NOT RECOMMENDED)", action="store_true")
    return parser.parse_args()

def start(autorestart):
    clear_screen()
    interpreter = sys.executable

    if interpreter is None:
        raise RuntimeError("Couldn't find Python's interpreter")

    #if verify_requirements() is None:
    #    print("You don't have the requirements to start Red. "
    #          "Install them from the launcher.")
    #    if not INTERACTIVE_MODE:
    #        exit(1)

    cmd = (interpreter, "bot.py")

    while True:
        try:
            code = subprocess.call(cmd)
        except KeyboardInterrupt:
            code = 0
            break
        else:
            if code == 0:
                break
            elif code == 26:
                print("Restarting VectorBot...")
                continue
            else:
                if not autorestart:
                    break

    print("VectorBot has been terminated. Exit code: %d" % code)

    if INTERACTIVE_MODE:
        wait()

def update():
    try:
        code = subprocess.call(("git", "pull", "--ff-only"))
    except FileNotFoundError:
        print("\nError: Git not found. It's either not installed or not in the PATH environment variable like requested in the guide.")
        return
    if code == 0:
        print("\nVectorBot has been updated")
    else:
        print("\nVectorBot could not be updated properly. If you made edits to the bot"
             " you can reset the bot.")

def update_reqs():
    interpreter = sys.executable

    if interpreter is None:
        print("\n\033[31;37;1mPython interpreter not found.\033[0m")
        return
    
    args = [
        interpreter, '-m', 'pip', 'install',
        '--upgrade', '--target', LIB_DIR,
        '-r', 'requirements.txt'
    ]
    
    if IS_MAC: # Stolen from Red-DiscordBot PR #552
        args.remove("--target")
        args.remove(LIB_DIR)
    
    code = subprocess.call(args)
    
    if code == 0:
        print("\n\033[32mRequirements Installed\033[0m")
    else:
        print("\n\033[31;37;1mAn error occurred while installing the requirements\033[0m")

def reset():
    try:
        code = subprocess.call(("git", "pull", "--ff-only"))
    except FileNotFoundError:
        print("\n\033[31;37;1mError: Git not found. It's either not installed or not in the PATH environment variable like requested in the guide.\033[0m")
        return
    if code == 0:
        print("\n\033[32mVectorBot has been updated\033[0m")
    else:
        print("\n\033[31;37;1mVectorBot could not be updated properly."
              "If you made edits to the bot you can reset the bot.\033[0m")

def user_choice():
    return input("> ").lower().strip()

def is_git_installed():
    try:
        subprocess.call(["git", "--version"], stdout=subprocess.DEVNULL,
                                              stdin =subprocess.DEVNULL,
                                              stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return False
    else:
        return True

def clear_screen():
    if IS_WINDOWS:
        os.system("cls")
    else:
        os.system("clear")

def wait():
    if INTERACTIVE_MODE:
        input("Press enter to continue.")

def main():
    print("Verifying git installation...")
    has_git = is_git_installed()
    is_git_installation = os.path.isdir(".git")
    if IS_WINDOWS:
        os.system("TITLE [VectorBot] Launcher")
    clear_screen()

    while True:
        print(INTRO)

        if not is_git_installation:
            print("[WARNING]: It doesn't look like VectorBot has been installed with git.\n")

        if not has_git:
            print("[WARNING]: Git not found. This means that it's either not "
                  "installed or not in the PATH environment variable.\n")

        print("1. \033[32mRun VectorBot + autorestart\033[0m")
        print("2. \033[32mRun VectorBot\033[0m")
        print("3. \033[36mUpdate Vector Bot\033[0m")
        print("4. \033[31mReset VectorBot\033[0m")
        if pip is not None:
            print("5. \033[33mInstall Requiements\033[0m")
        print("\n0. Quit")
        choice = user_choice()
        if choice == "1":
            start(autorestart=True)
        elif choice == "2":
            start(autorestart=False)
        elif choice == "3":
            update()
        elif choice == "4":
            reset()
        elif choice == "5":
            if pip is not None:
                update_reqs()
        elif choice == "0":
            break
        clear_screen()

args = parse_cli_args()

if __name__ == '__main__':
    abspath = os.path.abspath(__file__)
    dirname = os.path.dirname(abspath)
    os.chdir(dirname)
    if not PYTHON_OK:
        print("Please use python3.5 or higher")
        sys.exit(1)
    if pip is None:
        print("pip not found, disabling auto update and red compatability features")
    if args.reset:
        reset()
    if args.update:
        update()
    if args.update_reqs:
        update_reqs()
    if INTERACTIVE_MODE:
        main()
    elif args.start:
        print("Starting VectorBot")
        start(autorestart=args.auto_restart)