import os
import sys

os.chdir(os.path.dirname(sys.argv[0]))

print("Ansura Setup")


def _hr():
    print("-" * 20)


resp = 0
while True:
    _hr()
    while True:
        print("Select an option\n"
              "1 - Update\n"
              "2 - Run Ansura\n"
              "3 - Run Ansura with Auto Restart\n"
              "4 - Initial setup\n"
              "9 - Quit")
        try:
            resp = int(input())
            if resp in [1, 2, 3, 4, 9]:
                break
        except ValueError:
            continue

    _hr()
    if resp == 1:
        os.system("git pull")

    elif resp == 2:
        print(f"Found python : {sys.executable}")
        print(f"Running {sys.executable} main.py")
        os.system(f"{sys.executable} main.py")

    elif resp == 3:
        while True:
            print(f"Found python : {sys.executable}")
            print(f"Running {sys.executable} main.py")
            os.system(f"{sys.executable} main.py")

    elif resp == 4:
        print(f"Found python : {sys.executable}")
        print(f"Running {sys.executable} -m pip install -U -r requirements.txt")
        os.system(f"{sys.executable} -m pip install -U -r requirements.txt")

        print("Initializing YAML Files")


    elif resp == 9:
        break
