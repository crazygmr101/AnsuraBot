import os
import sqlite3
import sys

os.chdir(os.path.dirname(sys.argv[0]))

print("Ansura Setup")

SQL_STRING = """
CREATE TABLE IF NOT EXISTS "bios" (
      "id" INTEGER NOT NULL,
      "bio" TEXT,
      PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "gaming" (
      "id"  int NOT NULL,
      "mojang"  varchar,
      "xboxlive"  varchar,
      "youtube"  varchar,
      "twitch"  varchar,
      "mixer"  varchar,
      "reddit"  varchar,
      "steam"  varchar,
      "private"  INTEGER NOT NULL DEFAULT 0,
      "webprivate"  INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS messages(
      id int not null,
      timestamp int not null);
CREATE TABLE IF NOT EXISTS "oauth" (
      "userid"INTEGER NOT NULL,
      "access_token"TEXT NOT NULL,
      PRIMARY KEY("userid")
);
CREATE TABLE IF NOT EXISTS "streamer" (
      "guildid"INTEGER NOT NULL,
      "streamrole"INTEGER NOT NULL,
      "streammsg"TEXT NOT NULL,
      "streamchannel"INTEGER NOT NULL,
      PRIMARY KEY("guildid")
);
CREATE TABLE IF NOT EXISTS "timezones" (
      "user"INTEGER UNIQUE,
      "timezone"TEXT,
      PRIMARY KEY("user")
)
"""


def _hr():
    print("-" * 20)


resp = 0
while True:  # noqa c901
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

        print(f"Found python : {sys.executable}")
        print(f"Running {sys.executable} -m pip install -U -r requirements.txt")
        os.system(f"{sys.executable} -m pip install -U -r requirements.txt")

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
        if input("Initialize configs? This will reset some things. [y/n]") != "y":
            continue

        print(f"Found python : {sys.executable}")
        print(f"Running {sys.executable} -m pip install -U -r requirements.txt")
        os.system(f"{sys.executable} -m pip install -U -r requirements.txt")

        print("Initializing YAML Files")
        with open("xchat.yaml", "w") as fp, open("xchat-default.yaml", "r") as fp2:
            fp.write(fp2.read())

        print("Initializing Database")
        conn: sqlite3.Connection = sqlite3.connect("users.db")
        cursor: sqlite3.Cursor = conn.cursor()
        for s in SQL_STRING.split(";"):
            print(" ".join(ln.strip() for ln in s.splitlines(False)))
            cursor.execute(s)
        conn.commit()
        conn.close()

        with open(".env", "w") as fp:
            for i, v in {
                "ANSURA": "discord bot token",
                "TWITCH": "twitch application token",
                "MIXER": "mixer token",
                "PASTEBIN": "pastebin token"
            }.items():
                fp.write(f"{i}={input(f'Input {v}: ')}\n")

    elif resp == 9:
        break
