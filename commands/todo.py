import os

if __name__ == "__main__:"
    if os.path.isfile("todo.txt"):
        with open("todo.txt", "r") as file:
            content = file.read()
            print(content)
    else:
        print("No todo.txt file detected")

