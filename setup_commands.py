import json
import os
import sys
from pprint import pprint

import dotenv
import requests
import glob

dotenv.load_dotenv(".env")

api_base = "https://discord.com/api/v8"
headers = {
    "Authorization": f"Bot {os.getenv('ANSURA')}"
}

# grab bot application id
application_id = requests.get(f"{api_base}/users/@me", headers=headers).json()["id"]
commands = []

for fn in glob.glob("commands/*.json"):
    with open(fn) as fp:
        commands += json.load(fp)["commands"]

if len(sys.argv) == 1 or sys.argv[1] not in ["--global", "--guild", "--clear"]:
    print("setup_commands.py - Load Ansura's commands from commands/*.json\n"
          "  --clear - clear all guilds\n"
          "  --clear 123456789 - clear guild with id 123456789\n"
          "  --global - deploy commands globally\n"
          "  --guild 123456789 - deploy commands to guild with id 123456789\n\n"
          "NOTE:\n"
          "  - using --global and --guild can lead to command duplication\n"
          "  - currently, discord only allows 200 command creations per guild per day")
    exit(0)

if sys.argv[1] == "--clear":
    if len(sys.argv) > 2:
        guild = sys.argv[2]
        url = f"{api_base}/applications/{application_id}/guilds/{guild}/commands"
        commands = []
    else:
        url = f"{api_base}/applications/{application_id}/commands"
        commands = []

elif sys.argv[1] == "--global":
    url = f"{api_base}/applications/{application_id}/commands"
else:
    guild = sys.argv[2]
    url = f"{api_base}/applications/{application_id}/guilds/{guild}/commands"

# get current commands for the guild
current_commands = requests.get(url, headers=headers).json()

current_command_names = {command["name"] for command in current_commands}
current_commands_indexed = {command["name"]: command for command in current_commands}

commands_names = {command["name"] for command in commands}
commands_indexed = {command["name"]: command for command in commands}

to_add = commands_names - current_command_names
to_delete = current_command_names - commands_names
to_overwrite = commands_names.intersection(current_command_names)

for name in to_add:
    print(f"Adding {name}...", end="")
    resp = requests.post(url,
                         json=commands_indexed[name],
                         headers={"Content-Type": "application/json",
                                  "Authorization": f"Bot {os.getenv('ANSURA')}"})
    print(resp.status_code)
    if resp.status_code >= 300:
        print()
        pprint(resp.json())
        resp.raise_for_status()

for name in to_delete:
    print(f"Deleting {name}...", end="")
    resp = requests.delete(url + "/" + current_commands_indexed[name]['id'],
                           headers=headers)
    print(resp.status_code)
    if resp.status_code >= 300:
        print()
        pprint(resp.json())
        resp.raise_for_status()

for name in to_overwrite:
    print(f"Overwriting {name}...", end="")
    resp = requests.patch(url + "/" + current_commands_indexed[name]['id'],
                          headers=headers, json=commands_indexed[name])
    print(resp.status_code)
    if resp.status_code >= 300:
        print()
        pprint(resp.json())
        resp.raise_for_status()
