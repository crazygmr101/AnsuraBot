import sqlite3
from typing import List, Dict

SQL_STRING="""
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
);
CREATE TABLE IF NOT EXISTS "prefixes" (
    "guild" INTEGER UNIQUE,
    "prefix" TEXT
)
"""


class AnsuraDatabase:
    def __init__(self):
        print("[DATABASE] Loading database")
        self.conn: sqlite3.Connection = sqlite3.connect("users.db")
        self.cursor: sqlite3.Cursor = self.conn.cursor()
        self.conn.executescript(SQL_STRING)

        r = self.cursor.execute("select * from prefixes").fetchall()
        self.prefixes: Dict[int, str] = {int(row[0]): row[1] for row in r}

        print("[DATABASE] Loaded database")

    def get_prefix(self, guild: int) -> str:
        return self.prefixes.get(guild, "%")

    def set_prefix(self, guild: int, prefix: str):
        if guild in self.prefixes:
            self.conn.execute("update prefixes set prefix=? where guild=?", (prefix, guild))
        else:
            self.conn.execute("insert into prefixes values (?,?)", (guild, prefix))
        self.conn.commit()
        self.prefixes[guild] = prefix

    def isprivate(self, userid: int):
        """
        :param userid:
        :return: private, webprivate
        """
        if not self.has_gaming_record(userid):
            self.add_gaming_record(userid)
        r = self.cursor.execute("select private,webprivate from gaming where id=?", (userid,)).fetchone()
        return r[0], r[1]

    def setprivate(self, userid: int, *, web: bool = None, gt: bool = None):
        if web is not None and gt is not None:
            raise AttributeError("web and gt can not be both supplied")
        if not self.has_gaming_record(userid):
            self.add_gaming_record(userid)
        if web is not None:
            self.cursor.execute("update gaming set webprivate=? where id=?", (1 if web else 0, userid))
        else:
            self.cursor.execute("update gaming set private=? where id=?", (1 if gt else 0, userid))
        self.conn.commit()
        return self.isprivate(userid)

    def get_bio(self, userid: int):
        row = self.cursor.execute("select * from bios where id=?", (userid,)).fetchone()
        if not row:
            return None
        return row[1]

    def set_bio(self, userid: int, bio: str):
        row = self.cursor.execute("select * from bios where id=?", (userid,)).fetchone()
        if row:
            self.cursor.execute("update bios set bio=? where id=?", (bio, userid))
        else:
            self.cursor.execute("insert into bios values (?,?)", (userid, bio))
        self.conn.commit()

    def lookup_timezone(self, userid: int):
        if not self.has_timezone(userid):
            self.add_timezone(userid)
        return self.cursor.execute("select * from timezones where user=?", (userid,)).fetchone()

    def add_timezone(self, userid: int):
        self.cursor.execute("insert into timezones values (?,?)", (userid, None))
        print("Empty tz record added for user " + str(userid))
        self.conn.commit()

    def set_timezone(self, userid: int, tz: str):
        if not self.has_timezone(userid):
            self.add_timezone(userid)
        self.cursor.execute("update timezones set timezone=? where user=?", (tz, userid))
        self.conn.commit()

    def has_timezone(self, userid: int):
        assert userid is not None
        return self.cursor.execute("select * from timezones where user=?", (userid,)).fetchone() is not None

    def add_gaming_record(self, userid: int):
        self.cursor.execute("insert into gaming values (?,?,?,?,?,?,?,?,?,?)",
                            (userid, None, None, None, None, None, None, None, 0, 1))
        print("Empty record added for user " + str(userid))
        self.conn.commit()

    def has_gaming_record(self, userid: int):
        assert userid is not None
        return self.cursor.execute("select * from gaming where id=?", (userid,)).fetchone() is not None

    def set_gaming_record(self, userid: int, type: str, string: str):
        if not self.has_gaming_record(userid):
            self.add_gaming_record(userid)
        self.cursor.execute("update gaming set " + type + "=? where id=?", (string, userid))
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
