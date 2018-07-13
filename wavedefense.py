import pygame
from pygame.locals import *
import json
import gamestates

class Game:
    def __init__(self):
        #self.state=gamestates.MainMenu(self)
        self.keys=[]
        self.data={}###TODO: load from JSON
        self.data["player_ship"]={}
        self.data["player_ship"]["path"]="saves/ship3.json"
        self.data["player_ship"]["data"]=[10,10,1,5,150,100,270,180,20,720]
        self.data["ships"]={}
        self.data["ships"]["e1"]={}
        self.data["ships"]["e1"]["path"]="saves/enemy1.json"
        self.data["ships"]["e1"]["data"]=[5,15,10,20,170,60,230,180,20,660]
        #self.data["enemies"][0]=
        
        self.state=gamestates.EvoArenaState(self)

    def loop(self,app,event):
        self.keys=pygame.key.get_pressed()
        for e in event:
            if e.type==pygame.QUIT:
                app.running=False
        self.state.loop(self,app,event)

    def render(self,app):
        window=app.window
        self.state.render(window)

        #render stuff!
