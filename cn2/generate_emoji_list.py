import json
# using json because idc

URL = 'https://unicode.org/Public/emoji/13.1/emoji-sequences.txt'

types = {
    "Basic_Emoji",
    "Emoji_Keycap_Sequence",
    "RGI_Emoji_Flag_Sequence",
    "RGI_Emoji_Tag_Sequence",
    "RGI_Emoji_Modifier_Sequence"
}

import urllib.request

with urllib.request.urlopen(URL) as response:
    raw = response.read().decode('utf-8')

emoji = []

for line in raw.split("\n"):

    if not line or line[0] == "#":
        continue
    code_point, type_field, *_ = [x.strip() for x in line.split("; ")]
    if type_field not in types:
        continue
    if ".." in code_point:  
        # add an emote with format ``23E9..23EC`` 
        lo, hi = code_point.split("..")
        emoji.extend([chr(x) for x in range(int(lo, 16), int(hi, 16) + 1)])
    else:                   
        # add an emote with format ``0035 FE0F 20E3``
        emoji.append("".join([chr(int(x, 16)) for x in code_point.split()]))

with open("emoji.json", "w", encoding='utf-8') as f:
    json.dump(emoji, f, skipkeys=False)
