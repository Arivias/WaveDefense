import pygame
import vecrig as vr
from pygame.locals import *
import math
import wdcore as wd
import inputmanagers
import weapons
import random

class TestState(wd.GameState):
    def __init__(self,game):
        super().__init__(game)
        self.screenpos=[-1000,-500]
        self.wscale=0.15
        self.s1=wd.Ship("saves/ship3.json",[1,10,1,5,150,100,270,180,20,720])
        self.s1.rig.y=10
        self.s1.rig.wscale=self.wscale
        self.s1.rig.screenpos=self.screenpos
        self.world=wd.GameWorld(2000)
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
        self.wscale=0.15
        self.screenpos=[(-960/2)/self.wscale,(-540/2)/self.wscale]
        self.world=wd.GameWorld(2000)
        self.posVelocity=[0,0]
        self.inputManagers=[]
        self.panTarget=-1
        self.scores=[]
        self.maxTime=20
        self.cTime=0
        self.currentGeneration=0

        ####Test stuff
        #self.world.shipList=[wd.Ship(game.data["ships"]["e1"]["path"],game.data["ships"]["e1"]["data"],"player",self.world)]
        #self.world.shipList[0].weapons[0].append(weapons.wp_PulseLaser(self.world.shipList[0],3,"weapon1",self.world))
        #self.world.rigs=[self.world.shipList[0].rig]
        #self.world.tickQueue=[self.world.shipList[0]]
        #self.inputManagers=[inputmanagers.PlayerInputManager()]
        #self.world.shipList.append(wd.Ship("saves/ship4.json",game.data["player_ship"]["data"],"enemy",self.world))
        #self.world.rigs.append(self.world.shipList[1].rig)
        #self.world.tickQueue.append(self.world.shipList[1])
        #self.world.shipList[1].weapons[0].append(weapons.wp_PulseLaser(self.world.shipList[1],0,"weapon1",self.world))
        #self.inputManagers.append(inputmanagers.EvoAIInput())
        #self.world.shipList[1].aiControllerCallback=self.inputManagers[1]

        self.numShips=6
        self.controllers=[]
        angle=0
        angleInc=math.pi*2/self.numShips
        for i in range(self.numShips):
            pos=[self.world.radius*0.75,0]
            sp=[0,0]
            sp[0]=pos[0]*math.cos(angle)-pos[1]*math.sin(angle)
            sp[1]=pos[0]*math.sin(angle)+pos[1]*math.cos(angle)
            s=wd.Ship(game.data["ships"]["e1"]["path"],game.data["ships"]["e1"]["data"],"enemy"+str(i),self.world)
            s.weapons[0].append(weapons.wp_PulseLaser(s,1,"weapon1",self.world))
            s.rig.x=sp[0]
            s.rig.y=sp[1]
            s.rig.rot=math.pi*2*random.randint(0,100)/100
            i=inputmanagers.EvoAIInput()
            s.aiControllerCallback=i
            self.inputManagers.append(i)
            self.world.shipList.append(s)
            self.world.rigs.append(s.rig)
            self.world.tickQueue.append(s)
            angle+=angleInc
        
    def loop(self,game,app,event):
        self.cTime+=app.deltaTime
        if len(self.world.shipList)<=1 or self.cTime>=self.maxTime:
            self.cTime=0
            angle=0
            angleInc=math.pi*2/self.numShips
            for i in range(len(self.inputManagers)):
                self.scores.append((self.inputManagers[i].score,self.inputManagers[i]))
            bestScore=self.scores[0][0]
            bi=0
            for i in range(len(self.scores)):
                if self.scores[i][0]>bestScore:
                    bestScore=self.scores[i][0]
                    bi=i
            #bestScore=self.msortScores(self.scores)
            ########
            self.world.shipList=[]
            self.world.tickQueue=[]
            self.world.rigs=[]
            self.inputManagers=[]
            for i in range(self.numShips):
                pos=[self.world.radius*0.75,0]
                sp=[0,0]
                sp[0]=pos[0]*math.cos(angle)-pos[1]*math.sin(angle)
                sp[1]=pos[0]*math.sin(angle)+pos[1]*math.cos(angle)
                s=wd.Ship(game.data["ships"]["e1"]["path"],game.data["ships"]["e1"]["data"],"enemy"+str(i),self.world)
                s.weapons[0].append(weapons.wp_PulseLaser(s,1,"weapon1",self.world))
                s.rig.x=sp[0]
                s.rig.y=sp[1]
                s.rig.rot=math.pi*2*random.randint(0,100)/100
                i=inputmanagers.EvoAIInput(self.scores[bi][1])
                s.aiControllerCallback=i
                self.inputManagers.append(i)
                self.world.shipList.append(s)
                self.world.rigs.append(s.rig)
                self.world.tickQueue.append(s)
                angle+=angleInc
            self.scores=[]
            
            print(str(self.currentGeneration)+": "+str(bestScore))#[len(bestScore)-1][0]))
            self.currentGeneration+=1
        
            
        ##Pan camera
        if self.panTarget!=-1:
            screenwidth=app.window.get_size()
            self.posVelocity[0]=self.world.shipList[self.panTarget].rig.x-(self.screenpos[0]+(screenwidth[0]/2)/self.wscale)
            self.posVelocity[1]=self.world.shipList[self.panTarget].rig.y-(self.screenpos[1]+(screenwidth[1]/2)/self.wscale)
            self.screenpos[0]+=self.posVelocity[0]*app.deltaTime
            self.screenpos[1]+=self.posVelocity[1]*app.deltaTime
        else:
            self.posVelocity=[0,0]
        
        for ship in range(len(self.world.shipList)):
            ip=self.inputManagers[ship].getInputArray(app.deltaTime,self,self.world.shipList[ship])
            if ip!=None:
                self.world.shipList[ship].input=ip
        delList=self.world.tick(app.deltaTime)
        if len(delList)>0:
            newInputs=[]
            for i in range(len(self.inputManagers)):
                if i in delList:
                    self.scores.append((self.inputManagers[i].score,self.inputManagers[i]))
                    continue
                newInputs.append(self.inputManagers[i])
            self.inputManagers=newInputs
                
    def render(self,window):
        self.world.render(window,self.screenpos,self.wscale)
    def msortScores(self,scores):
        if len(scores)<=1:
            return scores
        else:
            s1=self.msortScores(scores[:int(len(scores)/2)])
            s2=self.msortScores(scores[int(len(scores)/2):])
            out=[]
            while len(s1)!=0 and len(s2)!=0:
                if s1[0][0]>s2[0][0]:
                    out.append(s2.pop(0))
                else:
                    out.append(s1.pop(0))
            for s in s1:
                out.append(s)
            for s in s2:
                out.append(s)
            return out
    
class MainMenu(wd.GameState):
    def __init__(self,game):
        super().__init__(game)
        self.titleText=None#TODO: name game and create title vecrig
        
    def loop(self,game,app,event):
        pass

    def render(self,window):
        pass
