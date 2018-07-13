from abc import ABC, abstractmethod
import vecrig as vr
import math
import pygame

class GameState(ABC):
    def __init__(self,game):
        self.game=game
        self.wzoom=1
        self.wpos=[0,0]
    @abstractmethod
    def loop(self,app,event):
        pass
    @abstractmethod
    def render(self,window):
        pass

class Ship:
    def __init__(self,imgPath,shipData,team,world):
        self.rig=vr.Rig(imgPath)
        self.world=world
        self.data=shipData
        self.team=team
        self.aiControllerCallback=None
        #0 float value of max health
        #1 forward acceleration rate px/sec2 #
        #2 backward acceleration rate px/sec2 #
        #3 strafe acceleration rate px/sec2
        #5 x/y deceleration rate px/sec2
        #6 rotation acceleration rate deg/sec2
        #7 rotation deceleration rate deg/sec2
        #8 max x/y speed multiplier px/sec
        #9 max rotation speed deg/sec
        self.currentHealth=self.data[0]
        self.speed=[0,0,0]
        self.input=[0,0,0,0,0,0,0]
        self.weapons=[[],[]]#weapon slot 1, weapon slot 2
    def tick(self,deltaTime):
        #0 x movement fraction -1 to 1
        #1 y movement fraction -1 to 1
        #2 rotation speed fraction -1 to 1
        #3 weapon 1
        #4 weapon 2
        #5 ability 1
        #6 ability 2

        ####initial

        #speed decel
        decel_th=math.atan2(self.speed[1],self.speed[0])
        decel_x=self.data[4]*deltaTime*math.cos(decel_th)
        decel_y=self.data[4]*deltaTime*math.sin(decel_th)
        if self.speed[0]!=0:
            sign=self.speed[0]
            self.speed[0]-=math.copysign(decel_x,self.speed[0])
            if sign<0 and self.speed[0]>0:
                self.speed[0]=0
            elif sign>0 and self.speed[0]<0:
                self.speed[0]=0
        if self.speed[1]!=0:
            sign=self.speed[1]
            self.speed[1]-=math.copysign(decel_y,self.speed[1])
            if sign<0 and self.speed[1]>0:
                self.speed[1]=0
            elif sign>0 and self.speed[1]<0:
                self.speed[1]=0
        if self.speed[2]!=0:
            sign=self.speed[2]
            self.speed[2]-=math.copysign(self.data[7]*deltaTime,self.speed[2])
            if sign<0 and self.speed[2]>0:
                self.speed[2]=0
            elif sign>0 and self.speed[2]<0:
                self.speed[2]=0
            
        ####inputs

        ##movement
        m_worldAngle=math.atan2(self.input[1],self.input[0])+math.pi/2
        m_tAngle=(m_worldAngle-self.rig.rot)*-1
        m_total=0
        #forward
        m_segValue=self.data[1]*math.cos(m_tAngle)
        if m_segValue>0:
            m_total+=m_segValue
        #backward
        m_segValue=self.data[2]*-1*math.cos(m_tAngle)
        if m_segValue>0:
            m_total+=m_segValue
        #strafe
        m_segValue=self.data[3]*math.sin(m_tAngle)
        m_total+=math.fabs(m_segValue)
        m_inputSpeed=[m_total*math.sin(m_worldAngle),m_total*math.cos(m_worldAngle)]
        m_inputSpeed[1]=math.copysign(m_inputSpeed[1],self.input[1])

        m_speedOld=[self.speed[0],self.speed[1]]
        self.speed[0]+=m_inputSpeed[0]*math.fabs(self.input[0])
        self.speed[1]+=m_inputSpeed[1]*math.fabs(self.input[1])
        
        m_h=math.hypot(self.speed[0],self.speed[1])
        m_max=m_total*self.data[8]
        if m_h>m_max:
            m_total=m_max-math.hypot(m_speedOld[0],m_speedOld[1])
            m_total=max(m_total,0)
            m_inputSpeed=[m_total*math.sin(m_worldAngle),m_total*math.cos(m_worldAngle)]
            m_inputSpeed[1]=math.copysign(m_inputSpeed[1],self.input[1])
            self.speed[0]=m_speedOld[0]+m_inputSpeed[0]*math.fabs(self.input[0])
            self.speed[1]=m_speedOld[1]+m_inputSpeed[1]*math.fabs(self.input[1])
        m_h=math.fabs(math.hypot(self.speed[0],self.speed[1]))
            
        ##rotation
        self.speed[2]+=self.data[6]*self.input[2]*deltaTime
        m_r=math.fabs(self.speed[2])
        if m_r>self.data[9]:
            m_r=self.data[9]
            self.speed[2]=math.copysign(m_r,self.speed[2])

        ####weapons
        for category in self.weapons:
            for w in category:
                w.tick(deltaTime)
        if self.input[3]>0:
            for w in self.weapons[0]:
                w.fire()

        ####apply updates
        #print(self.speed[0])
        self.rig.x+=self.speed[0]*deltaTime
        self.rig.y+=self.speed[1]*deltaTime
        self.rig.rotateBy(math.radians(self.speed[2])*deltaTime)
    
    def damage(self,amount):
        self.currentHealth-=amount
        if self.currentHealth<=0:
            self.world.deleteQueue.append(self)
        if self.aiControllerCallback!=None:
            self.aiControllerCallback.score-=amount/2

class GameWorld:
    def __init__(self,radius):
        self.radius=radius
        self.rigs=[]
        self.tickQueue=[]
        self.shipList=[]
        self.deleteQueue=[]
        #self.grid=[[],[]]
        #self.gridwidth=100
    def tick(self,deltaTime):
        for obj in self.tickQueue:
            obj.tick(deltaTime)
        for ship in self.shipList:
            if math.hypot(ship.rig.x,ship.rig.y)>self.radius:
                angle=math.atan2(ship.rig.y,ship.rig.x)
                ship.rig.x=self.radius*math.cos(angle)
                ship.rig.y=self.radius*math.sin(angle)
                ship.speed[0]*=math.sin(angle)
                ship.speed[1]*=math.cos(angle)
        delList=[]
        for obj in range(len(self.deleteQueue)):
            if self.deleteQueue[obj] in self.shipList:
                self.rigs.remove(self.deleteQueue[obj].rig)
                self.shipList.remove(self.deleteQueue[obj])
                self.tickQueue.remove(self.deleteQueue[obj])
                delList.append(obj)
            if self.deleteQueue[obj] in self.rigs:
                self.rigs.remove(self.deleteQueue[obj])
            if self.deleteQueue[obj] in self.tickQueue:
                self.tickQueue.remove(self.deleteQueue[obj])
        self.deleteQueue=[]
        return delList
    def render(self,window,screenpos=[0,0],wscale=1):
        pygame.draw.circle(window,(0,255,0),[int(-1*screenpos[0]*wscale),int(-1*screenpos[1]*wscale)],int(self.radius*wscale),1)
        #grid?
        for rig in self.rigs:
            rig.screenpos=screenpos
            rig.wscale=wscale
            rig.render(window)
class Projectile:
    def __init__(self,world,team,ship):
        self.rig=None
        self.world=world
        self.team=team
        self.ship=ship
    def tick(self,deltaTime):
        pass
    def rewardCreator(self,val):
        if self.ship.aiControllerCallback!=None:
            self.ship.aiControllerCallback.score+=val
class Weapon:
    def __init__(self,name,ship,category,world):
        self.ship=ship
        self.world=world
        self.name=name
        self.wpoints=[]
        for pt in ship.rig.points:
            if category in pt.tags:
                self.wpoints.append(pt)
        pass
    def fire(self):
        pass
    def tick(self,deltaTime):
        pass
