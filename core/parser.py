from pathlib import Path

class Parser:
    def __init__(self):
        txt = Path("Assets/words.txt").read_text()
        self.arr = txt.split("\n")
        self.words = dict()
        for s in self.arr:
            self.words[s.split(',')[0]] = s.split(',')[1]
        print(self.words)

    def simplify(self, string: str):
        sar = string[1:].lower().split(" ")
        st = []
        for s in sar:
            if s not in self.words:
                st.append(s)
            else:
                if self.words[s] != "#":
                    st.append(self.words[s])
        return " ".join(st)