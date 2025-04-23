import os

print("Authorizing build, run, and clean shell scripts...")
os.system("chmod +x build.sh")
os.system("chmod +x run.sh")
os.system("chmod +x clean.sh")
print("Finished!")