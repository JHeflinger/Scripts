import urllib.request

if __name__ == "__main__":
    try:
        urllib.request.urlretrieve("https://raw.githubusercontent.com/JHeflinger/Scripts/refs/heads/main/shell.py", "shell.py")
        print("Successfully updated shell to current working directory!")
    except:
        print("Failed to update shell into current working directory. Are you sure you are connected to the internet?")
