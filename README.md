[ULTRASHELL](https://github.com/JHeflinger/shell) - One internal tool to rule them all!
=======================================================

## INFO

Ultrashell is a shell program that allows you to run any internal tool from this repository! Alone, ultrashell only contains itself, the ability to use git, clear screen, and run run/build/clean scripts you've defined. However, if you attempt to use any other command, it will fetch it from this remote repository and dynamically store it in a cache in the working directory! With the power of ultrashell, you can use just the internal tools you need when you need them!
> NOTE: Ultrashell fetches from this repository! If you'd like to customize it to fetch from somewhere else, modify the `download()` function in `shell.py` to update your remote location.

## REQUIREMENTS

All ultrashell requires is python! It was developed on python 3.10, so to ensure best compatibility try and run it close to that version! The commands, however, may require other dependencies, so beware!

## HOW TO USE

All you have to do to use the shell is run `shell.py` from your working directory! That's it!
