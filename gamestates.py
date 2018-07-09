import pygame
import vecrig as vr
from pygame.locals import *
import math
import wdcore as wd

class TestState(wd.GameState):
    def __init__(self,game):
        super().__init__(game)
        self.screenpos=[0,0]
        self.wscale=1.0
        self.s1=wd.Ship("saves/ship3.json",[1,10,2,5,150,360,180,180,50,180])
        self.s1.rig.y=10
        self.s1.speed=[300,200,370]
        #self.debug=0
        
    def loop(self,game,app,event):
        self.s1.update([0,1],app.deltaTime)
        #d=[(0-10*math.sin(self.debug))*0.5,(10*math.cos(self.debug))*1]
        #print(math.hypot(d[0],d[1]))
        #self.debug+=math.pi*app.deltaTime
        pass
    def render(self,window):
        self.s1.rig.render(window)
        pass
    
class MainMenu(wd.GameState):
    def __init__(self,game):
        super().__init__(game)
        self.titleText=None#TODO: name game and create title vecrig
        
    def loop(self,game,app,event):
        pass

    def render(self,window):
        pass
