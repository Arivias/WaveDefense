import os

i=input("delete saved data[y/n]? ")
if i=="y":
    os.remove("saves/Gamedata/gamestate.json")
