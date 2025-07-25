"""
author: Jason Heflinger
description: Runs a customized shell program to grow and download custom commands from
             a custom scripts repository.
"""
import sys
import os
import urllib.request
last_modified = "7/25/2025"
version = "version 1.0.1"

def gstr(str):
    return "\033[32m" + str + "\033[0m"

def sysprompt():
    print(f"Ultrashell {gstr(version)} authored by Jason Heflinger (https://github.com/JHeflinger)")
    print("Developed on Python 3.10")
    print(f"Last modified on {gstr(last_modified)}")
    print("Enter command \"help\" for usage details")

def printhelp():
    print(f"\nWelcome to \033[32mULTRASHELL\033[0m, an ultimate and versatile dev tool!\n")
    print("This program exists to simplify, condense, and scale existing build tools and scripts across projects!")
    print("When in the shell, you will be able to download scripts and dynamically set up dev tools!")
    print("\nBy default, the script database is set up to be my own personal script database.")
    print("If you'd like to use your own, then you can pass in a web hosted directory link via the first argument of the shell.")
    print("\nUsage:\n\tshell.py <url>")
    print("\nIf you're using ultrashell via the installer, then edit DB.txt file from the installation directory.")
    print("\nBy default, ultrashell is shipped with the following default commands:\n")
    print("\tgit <args...> | All git functions (requires git to be installed)")
    print("\tclear         | Clears the console")
    print("\tquit          | Exits ultrashell")
    print("\thelp          | Displays this message")
    print("\trun           | Attempts to run a run.sh or run.bat script (Depending on OS)")
    print("\tbuild         | Attempts to run a build.sh or build.bat script (Depending on OS)")
    print("\tclean         | Attempts to run a clean.sh or clean.bat script (Depending on OS)")
    print("\nIf you don't have a given command downloaded, then try it anyway and follow the prompts to download it into your script cache!")

def download(command):
    staticlink = "https://raw.githubusercontent.com/JHeflinger/Scripts/refs/heads/main/commands"
    if len(sys.argv) > 1:
        staticlink = sys.argv[1]
    try:
        urllib.request.urlretrieve(f"{staticlink}/{command}.py", f".scache/{command}.py")
    except:
        return False
    return True

def initcache():
    if os.path.isdir(".scache"):
        return True
    print("No script cache has been set up yet. Would you like to set one up now? (y/n)")
    response = ""
    while True:
        response = input("> ")
        if (response.lower() == "y" or response.lower() == "n"):
            response = response.lower()
            break
        else:
            print(f"Invalid response \"{response}\" detected. Please enter either \"y\" or \"n\".")
    if (response == "n"):
        return False 
    os.makedirs(".scache", exist_ok=True)
    if os.path.isdir(".git"):
        print("Current directory is a git repository. Would you like to add the script cache to .gitignore? (y/n)")
        response = ""
        while True:
            response = input("> ")
            if (response.lower() == "y" or response.lower() == "n"):
                response = response.lower()
                break
            else:
                print(f"Invalid response \"{response}\" detected. Please enter either \"y\" or \"n\".")
        if (response == "y"):
            print("Adding to .gitignore...")
            with open(".gitignore", "a") as f:
                f.write("\n.scache/*\n")
    print("Finished initializing script cache!")
    return True

def trycommand(script):
    if (not initcache()):
        print("Unable to find custom command in script cache.")
        return False
    if (os.path.isfile(f".scache/{script}.py")):
        return True
    print("Command was not found on disk. Would you like to attempt to download it? (y/n)")
    response = ""
    while True:
        response = input("> ")
        if (response.lower() == "y" or response.lower() == "n"):
            response = response.lower()
            break
        else:
            print(f"Invalid response \"{response}\" detected. Please enter either \"y\" or \"n\".")
    if (response == "y"):
        if download(script):
            print("Successfully downloaded command!")
            return True
        print("Unable to download command. Make sure you are connected to internet and that the command exists.")
        return False
    print("Unable to run command.")
    return False

def shell():
    cmd = ""
    while True:
        cmd = input("> ")
        topcmd = cmd.split(" ")[0]
        argind = cmd.find(" ")
        argstr = ""
        if (argind > 0):
            argstr = cmd[argind:]
        if (topcmd == "git" or topcmd == "g" or topcmd == "clear"):
            os.system(cmd)
        elif (topcmd == "help" or topcmd == "h"):
            printhelp()
        elif (topcmd == "build" or topcmd == "b"):
            if (os.name == "nt"):
                os.system("build.bat " + argstr)
            else:
                os.system("./build.sh" + argstr)
        elif (topcmd == "run" or topcmd == "r"):
            if (os.name == "nt"):
                os.system("run.bat " + argstr)
            else:
                os.system("./run.sh" + argstr)
        elif (topcmd == "clean" or topcmd == "c"):
            if (os.name == "nt"):
                os.system("clean.bat " + argstr)
            else:
                os.system("./clean.sh" + argstr)
        elif (cmd == "exit" or cmd == "quit" or cmd == "q" or cmd == "e"):
            break
        else:
            if (trycommand(topcmd)):
                os.system("python .scache/" + topcmd + ".py" + argstr)

def goodbye():
    print("Exiting Ultrashell...")

if __name__ == "__main__":
    sysprompt()
    shell()
    goodbye()
