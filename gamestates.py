import pygame
import vecrig as vr
from pygame.locals import *
import math
import wdcore as wd
import inputmanagers
import ai_controller
import weapons
import random

class DemoMenuState(wd.GameState):
    def __init__(self,game):
        super().__init__(game)
        
    def loop(self,game,app,event):
        pass
    def render(self,window):
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

        self.numShips=2
        #self.halfMode=False
        self.controllers=[]
        angle=0
        angleInc=math.pi*2/self.numShips
        startNetwork=None
        if "best_network" in game.data:
            startNetwork=game.data["best_network"]
        if "current_generation" in game.data:
            self.currentGeneration=game.data["current_generation"]
        for i in range(self.numShips):
            pos=[self.world.radius*0.75,0]
            sp=[0,0]
            sp[0]=pos[0]*math.cos(angle)-pos[1]*math.sin(angle)
            sp[1]=pos[0]*math.sin(angle)+pos[1]*math.cos(angle)
            s=wd.Ship(game.data["ships"]["e1"]["path"],game.data["ships"]["e1"]["data"],"enemy"+str(i),self.world)
            s.weapons[0].append(weapons.wp_PulseLaser(s,1,"weapon1",self.world))
            s.rig.x=sp[0]
            s.rig.y=sp[1]
            s.rig.rot=math.pi/2+angle#math.pi*2*random.randint(0,100)/100
            i=ai_controller.AIController(id=i)
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
            #for i in range(len(self.inputManagers)):
            #    self.scores.append((self.inputManagers[i].score,self.inputManagers[i]))
            #if not self.halfMode:
            #    bestScore=self.scores[0][0]
            #    bi=0
            #    for i in range(len(self.scores)):
            #        if self.scores[i][0]>bestScore:
            #            bestScore=self.scores[i][0]
            #            bi=i
            #else:
            #    self.bestScore=self.msortScores(self.scores)
            #    cb=0
            #    cu=0
            self.world.shipList=[]
            self.world.tickQueue=[]
            self.world.rigs=[]
            #self.inputManagers=[]
            for i in range(self.numShips):
                self.inputManagers[i].train(0.99)
                pos=[self.world.radius*0.75,0]
                spawn_position=[0,0]
                spawn_position[0]=pos[0]*math.cos(angle)-pos[1]*math.sin(angle)
                spawn_position[1]=pos[0]*math.sin(angle)+pos[1]*math.cos(angle)
                ship=wd.Ship(game.data["ships"]["e1"]["path"],game.data["ships"]["e1"]["data"],"enemy"+str(i),self.world)
                ship.weapons[0].append(weapons.wp_PulseLaser(ship,1,"weapon1",self.world))
                ship.rig.x, ship.rig.y = spawn_position
                ship.rig.rot=math.pi/2+angle#math.pi*2*random.randint(0,100)/100
                #if self.halfMode:
                #    net=self.bestScore[cb][1]
                #    if cu==1:
                #        cu=0
                #        cb+=1
                #    else:
                #        cu+=1
                #else:
                #    net=self.scores[bi][1]
                #i=ai_controller.AIController()#this just randomizes it
                ship.aiControllerCallback=self.inputManagers[i]
                #self.inputManagers.append(i)
                self.world.shipList.append(ship)
                self.world.rigs.append(ship.rig)
                self.world.tickQueue.append(ship)
                angle+=angleInc

            if self.currentGeneration%2==0 and False:####save frequency ######disabled
                if self.halfMode:
                    game.data["best_network"]=self.bestScore[len(self.bestScore)-1][1].weights
                else:
                    game.data["best_network"]=self.scores[bi][1].weights
                game.data["current_generation"]=self.currentGeneration
                game.save()
            self.scores=[]

            #if self.halfMode:
            #    print(str(self.currentGeneration)+": "+str(self.bestScore[len(self.bestScore)-1][0]))
            #else:
            #    print(str(self.currentGeneration)+": "+str(self.scores[bi][0]))
            print(self.currentGeneration)
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
            for i in range(len(self.inputManagers)):
                if i in delList:
                    self.inputManagers[i].getInputArray(app.deltaTime,self,self.world.shipList[ship],False)
                    continue
                
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
