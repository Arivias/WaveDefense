import pygame
import vecrig as vr
from pygame.locals import *
import math
import wdcore as wd
import inputmanagers
import ai_controller
import weapons
import random
import tensorflow as tf
import os

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
        self.wscale=0.12
        self.screenpos=[(-960/2)/self.wscale,(-540/2)/self.wscale]
        self.world=wd.GameWorld(2000)
        self.posVelocity=[0,0]
        self.inputManagers=[]
        self.panTarget=-1
        self.scores=[]
        self.maxTime=20
        self.cTime=0
        self.currentGeneration=0
        global_net = ai_controller.AINetwork('test')
        ai_controller.AIController.sess = tf.Session()
        self.saver = tf.train.Saver(max_to_keep=10)
        self.logo=vr.Rig("saves/Vector_Rigs/next.json")

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
        load = True
        try:
            folder_path='saves/Gamedata/ai-model'
            checkpoint = tf.train.get_checkpoint_state(folder_path)
            print('Checkpoint path:', os.path.abspath(checkpoint.model_checkpoint_path))
            #restore the checkpoint for our agent
            self.saver.restore(ai_controller.AIController.sess, os.path.abspath(checkpoint.model_checkpoint_path))
            print('Model restored.')
        except Exception as e:
            print('Did not load model.')
            print(e)
        
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
            s.rig.rot=math.pi/2+angle+math.pi*2*random.randint(0,100)/100
            i=ai_controller.AIController(ai_id=i)
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
                self.inputManagers[i].train(0.99,0.0)
                pos=[self.world.radius*0.75,0]
                spawn_position=[0,0]
                spawn_position[0]=pos[0]*math.cos(angle)-pos[1]*math.sin(angle)
                spawn_position[1]=pos[0]*math.sin(angle)+pos[1]*math.cos(angle)
                ship=wd.Ship(game.data["ships"]["e1"]["path"],game.data["ships"]["e1"]["data"],"enemy"+str(i),self.world)
                ship.weapons[0].append(weapons.wp_PulseLaser(ship,1,"weapon1",self.world))
                ship.rig.x, ship.rig.y = spawn_position
                ship.rig.rot=math.pi/2+angle+math.pi*2*random.randint(0,100)/100
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

            if self.currentGeneration%10==0:####save frequency ######disabled
                #######
                if not self.saver:
                    self.saver = tf.train.Saver(max_to_keep=10)
                folder_path='saves/Gamedata/ai-model/'
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                self.saver.save(ai_controller.AIController.sess, folder_path+'trained', global_step=self.currentGeneration)
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
        self.logo.y=-self.world.radius*1.5/3
        self.logo.screenpos=self.screenpos
        self.logo.wscale=self.wscale
        self.logo.scale=self.world.radius/2000*3
        self.logo.render(window)
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

class DemoArenaState(wd.GameState):####################################
    def __init__(self,game):
        super().__init__(game)
        self.wscale=0.12
        self.screenpos=[(-960/2)/self.wscale,(-540/2)/self.wscale]
        self.world=wd.GameWorld(2000)
        self.posVelocity=[0,0]
        self.inputManagers=[]
        self.panTarget=0
        self.scores=[]
        self.cTime=0
        global_net = ai_controller.AINetwork('test')
        ai_controller.AIController.sess = tf.Session()
        self.saver = tf.train.Saver(max_to_keep=10)
        self.logo=vr.Rig("saves/Vector_Rigs/next.json")

        self.numShips=1
        self.controllers=[]
        angle=0
        angleInc=math.pi*2/self.numShips
        load = True
        folder_path='saves/Gamedata/ai-model'
        checkpoint = tf.train.get_checkpoint_state(folder_path)
        print('Checkpoint path:', os.path.abspath(checkpoint.model_checkpoint_path))
        #restore the checkpoint for our agent
        self.saver.restore(ai_controller.AIController.sess, os.path.abspath(checkpoint.model_checkpoint_path))
        #create player ship
        s=wd.Ship(game.data["player_ship"]["path"],game.data["player_ship"]["data"],"player",self.world)
        s.rig.rot=math.pi/-2
        s.weapons[0].append(weapons.wp_PulseLaser(s,1,"weapon1",self.world))
        self.world.shipList.append(s)
        self.world.rigs.append(s.rig)
        self.world.tickQueue.append(s)
        self.inputManagers.append(inputmanagers.PlayerInputManager())
        print('Model restored.')
        for i in range(self.numShips):
            pos=[self.world.radius*0.75,0]
            sp=[0,0]
            sp[0]=pos[0]*math.cos(angle)-pos[1]*math.sin(angle)
            sp[1]=pos[0]*math.sin(angle)+pos[1]*math.cos(angle)
            s=wd.Ship(game.data["ships"]["e1"]["path"],game.data["ships"]["e1"]["data"],"enemy",self.world)
            s.weapons[0].append(weapons.wp_PulseLaser(s,1,"weapon1",self.world))
            s.rig.x=sp[0]
            s.rig.y=sp[1]
            s.rig.rot=math.pi/2+angle+math.pi*2*random.randint(0,100)/100
            i=ai_controller.AIController(ai_id=i)
            s.aiControllerCallback=i
            self.inputManagers.append(i)
            self.world.shipList.append(s)
            self.world.rigs.append(s.rig)
            self.world.tickQueue.append(s)
            angle+=angleInc
        
    def loop(self,game,app,event):
        self.cTime+=app.deltaTime
            
        ##Pan camera
        if self.panTarget!=-1:
            screenwidth=app.window.get_size()
            self.posVelocity[0]=self.world.shipList[self.panTarget].rig.x-(self.screenpos[0]+(screenwidth[0]/2)/self.wscale)
            self.posVelocity[1]=self.world.shipList[self.panTarget].rig.y-(self.screenpos[1]+(screenwidth[1]/2)/self.wscale)
            self.screenpos[0]+=self.posVelocity[0]*app.deltaTime
            self.screenpos[1]+=self.posVelocity[1]*app.deltaTime
        else:
            self.posVelocity=[0,0]

        ##input
        for ship in range(len(self.world.shipList)):
            ip=self.inputManagers[ship].getInputArray(app.deltaTime,self,self.world.shipList[ship])
            if ip!=None:
                self.world.shipList[ship].input=ip
        delList=self.world.tick(app.deltaTime,False)
        if len(delList)>0:
            newManagers=[]
            for i in range(len(self.inputManagers)):
                if i in delList:
                    self.inputManagers[i].getInputArray(app.deltaTime,self,self.world.shipList[ship],False)
                    del self.world.shipList[i]
                    continue
                newManagers.append(self.inputManagers[i])
            self.inputManagers=newManagers
            
        if len(self.world.shipList)<=1:#on round end
            print("\n\n")
            if isinstance(self.inputManagers[0],inputmanagers.PlayerInputManager):
                print("All enemies defeated.")
            else:
                print("You were defeated.")
            app.running=False
                
    def render(self,window):
        self.world.render(window,self.screenpos,self.wscale)
        self.logo.y=-self.world.radius*1.5/3
        self.logo.screenpos=self.screenpos
        self.logo.wscale=self.wscale
        self.logo.scale=self.world.radius/2000*3
        self.logo.render(window)
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
