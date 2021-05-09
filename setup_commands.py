import json
import os
import sys

import dotenv
import requests

dotenv.load_dotenv(".env")

api_base = "https://discord.com/api/v8"
headers = {
    "Authorization": f"Bot {os.getenv('ANSURA')}"
}

# grab bot application id
application_id = requests.get(f"{api_base}/users/@me", headers=headers).json()["id"]

with open("commands.json") as fp:
    commands = json.load(fp)["commands"]

if sys.argv[1] not in ["--global", "--guild"]:
    exit(-1)

if sys.argv[1] == "--global":
    exit(-1)

guild = sys.argv[2]

# get current commands for the guild
current_commands = requests.get(f"{api_base}/applications/{application_id}/guilds/{guild}/commands",
                                headers=headers).json()
current_command_names = {command["name"] for command in current_commands}
current_commands_indexed = {command["name"]: command for command in current_commands}

commands_names = {command["name"] for command in commands}
commands_indexed = {command["name"]: command for command in commands}

to_add = commands_names - current_command_names
to_delete = current_command_names - commands_names
to_overwrite = commands_names.intersection(current_command_names)

for name in to_add:
    print(f"Adding {name}...", end="")
    resp = requests.post(f"{api_base}/applications/{application_id}/guilds/{guild}/commands",
                         json=commands_indexed[name],
                         headers={"Content-Type": "application/json",
                                  "Authorization": f"Bot {os.getenv('ANSURA')}"})
    print(resp.status_code)
    resp.raise_for_status()

for name in to_delete:
    print(f"Deleting {name}...", end="")
    resp = requests.delete(f"{api_base}/applications/{application_id}/guilds/"
                           f"{guild}/commands/{current_commands_indexed[name]['id']}",
                           headers=headers)
    print(resp.status_code)
    resp.raise_for_status()

for name in to_overwrite:
    print(f"Overwriting {name}...", end="")
    resp = requests.patch(f"{api_base}/applications/{application_id}/guilds/"
                          f"{guild}/commands/{current_commands_indexed[name]['id']}",
                          headers=headers, json=commands_indexed[name])
    print(resp.status_code)
    resp.raise_for_status()
