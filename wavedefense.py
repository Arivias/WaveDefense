import pygame
from pygame.locals import *
import json
import gamestates

class Game:
    def __init__(self):
        #self.state=gamestates.MainMenu(self)
        self.state=gamestates.TestState(self)
        self.keys=[]
        self.data={}###TODO: load from JSON
        pass

    def loop(self,app,event):
        for e in event:
            if e.type==pygame.QUIT:
                app.running=False
        self.state.loop(self,app,event)
        self.keys=pygame.key.get_pressed()

    def render(self,app):
        window=app.window
        self.state.render(window)

        #render stuff!
