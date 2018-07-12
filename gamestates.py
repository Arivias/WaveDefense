import pygame
import vecrig as vr
from pygame.locals import *
import math
import wdcore as wd
import inputmanagers
import weapons

class TestState(wd.GameState):
    def __init__(self,game):
        super().__init__(game)
        self.screenpos=[-1000,-500]
        self.wscale=0.3
        self.s1=wd.Ship("saves/ship3.json",[1,10,1,5,150,100,270,180,20,720])
        self.s1.rig.y=10
        self.s1.rig.wscale=self.wscale
        self.s1.rig.screenpos=self.screenpos
        self.world=wd.GameWorld(800)
        self.s1.weapons[0].append(weapons.wp_PulseLaser(self.s1,10,"weapon1",self.world))
        self.inputman=playerinputmanager.PlayerInputManager()
        self.world.shipList.append(self.s1)
        #self.debug=0
        
    def loop(self,game,app,event):
        self.s1.update(self.inputman.getInputArray(app.deltaTime,self,self.s1),app.deltaTime)
        self.world.tick(app.deltaTime)
        #d=[(0-10*math.sin(self.debug))*0.5,(10*math.cos(self.debug))*1]
        #print(math.hypot(d[0],d[1]))
        #self.debug+=math.pi*app.deltaTime
        pass
    def render(self,window):
        self.s1.rig.render(window)
        self.world.render(window,self.screenpos,self.wscale)
        pass

class EvoArenaState(wd.GameState):
    def __init__(self,game):
        super().__init__(game)
        self.screenpos=[0,0]
        self.wscale=1
        self.world=wd.GameWorld(2000)
        self.posVelocity=[0,0]

        ####Test stuff
        self.world.shipList=[wd.Ship(game.data["player_ship"]["path"],game.data["player_ship"]["data"],"player")]
        self.world.shipList[0].weapons[0].append(weapons.wp_PulseLaser(self.world.shipList[0],10,"weapon1",self.world))
        self.world.rigs=[self.world.shipList[0].rig]
        self.world.tickQueue=[self.world.shipList[0]]
        self.inputManagers=[inputmanagers.PlayerInputManager()]

        
    def loop(self,game,app,event):
        ##Pan camera
        for ship in range(len(self.world.shipList)):
            self.world.shipList[ship].input=self.inputManagers[ship].getInputArray(app.deltaTime,self,self.world.shipList[ship])
        self.world.tick(app.deltaTime)
    def render(self,window):
        self.world.render(window,self.screenpos,self.wscale)
    
class MainMenu(wd.GameState):
    def __init__(self,game):
        super().__init__(game)
        self.titleText=None#TODO: name game and create title vecrig
        
    def loop(self,game,app,event):
        pass

    def render(self,window):
        pass
