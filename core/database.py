import sqlite3
from typing import Union, List, Dict
import datetime
import discord


class AnsuraDatabase:
    def __init__(self):
        self.conn: sqlite3.Connection = sqlite3.connect("users.db")
        self.cursor: sqlite3.Cursor = self.conn.cursor()

    def add_gaming_record(self, userid: int):
        self.cursor.execute("insert into gaming values (?,?,?,?,?,?)", (userid, None, None, None, None, None))
        print("Empty record added for user " + str(userid))
        self.conn.commit()

    def has_gaming_record(self, userid: int):
        assert userid is not None
        return self.cursor.execute("select * from gaming where id=?", (userid,)).fetchone() is not None

    def set_gaming_record(self, userid: int, type: str, string: str):
        if not self.has_gaming_record(userid):
            self.add_gaming_record(userid)
        self.cursor.execute("update gaming set "+type+"=? where id=?", (string,userid))
        print(type + "set to " + string + " for " + str(userid))
        self.conn.commit()

    def lookup_gaming_record(self, userid: int):
        if not self.has_gaming_record(userid):
            self.add_gaming_record(userid)
        return self.cursor.execute("select * from gaming where id=?", (userid,)).fetchone()

    def get_all(self) -> List[Dict]:
        recs = self.cursor.execute("select * from gaming").fetchall()
        r = []
        for i in recs:
            # id, mojang, xbox, youtube, twitch, mixer
            r.append({
                "id": i[0],
                "mojang": i[1],
                "xbox": i[2],
                "youtube": i[3],
                "twitch": i[4],
                "mixer": i[5]
            })
        return r