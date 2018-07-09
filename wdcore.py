from abc import ABC, abstractmethod
import vecrig as vr
import math

class GameState(ABC):
    def __init__(self,game):
        self.game=game
    @abstractmethod
    def loop(self,app,event):
        pass
    @abstractmethod
    def render(self,window):
        pass

class Ship:
    def __init__(self,imgPath,shipData):
        self.rig=vr.Rig(imgPath)
        self.data=shipData
        #0 float value of max health
        #1 forward acceleration rate px/sec2 #
        #2 backward acceleration rate px/sec2 #
        #3 strafe acceleration rate px/sec2
        #5 x/y deceleration rate px/sec2
        #6 rotation acceleration rate deg/sec2
        #7 rotation deceleration rate deg/sec2
        #8 max x/y speed px/sec
        #9 max rotation speed deg/sec
        self.currentHealth=self.data[0]
        self.speed=[0,0,0]
    def update(self,inputs,deltaTime):
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

        #movement
        m_worldAngle=math.atan2(inputs[1],inputs[0])+math.pi/2
        #m_worldAngle%=math.pi*2
        m_tAngle=(m_worldAngle-self.rig.rot)*-1
        m_total=0
        #forward
        m_segValue=self.data[1]*math.cos(m_tAngle)
        #TODO: remove x value from segval
        if m_segValue>0:#use only same axis as original?
            m_total+=m_segValue
        #backward
        m_segValue=self.data[2]*-1*math.cos(m_tAngle)
        if m_segValue>0:#use only same axis as original?
            m_total+=m_segValue
        #strafe
        m_segValue=self.data[3]*math.sin(m_tAngle)
        m_total+=math.fabs(m_segValue)#use only same axis as original?
        m_inputSpeed=[m_total*math.sin(m_worldAngle),m_total*math.cos(m_worldAngle)]
        m_inputSpeed[1]=math.copysign(m_inputSpeed[1],inputs[1])
        self.speed[0]+=m_inputSpeed[0]*math.fabs(inputs[0])
        self.speed[1]+=m_inputSpeed[1]*math.fabs(inputs[1])
        m_h=math.fabs(math.hypot(self.speed[0],self.speed[1]))
        if m_h>self.data[8]:
            m_h=self.data[8]
            angle=math.atan2(self.speed[1],self.speed[0])
            x=m_h*math.cos(angle)
            y=m_h*math.sin(angle)
            self.speed[0]=math.copysign(x,self.speed[0])
            self.speed[1]=math.copysign(y,self.speed[1])
            
        


        ####apply updates
        #print(self.speed[0])
        self.rig.x+=self.speed[0]*deltaTime
        self.rig.y+=self.speed[1]*deltaTime
        self.rig.rotateBy(math.radians(self.speed[2])*deltaTime)
