import pygame
from pygame.locals import *
import math
import random
import wdcore

class DummyInputManager:
    def __init__(self):
        pass
    def getInputArray(self,deltaTime,state,ship):
        return None

class PlayerInputManager:
    def __init__(self):
        pass
    def getInputArray(self,deltaTime,state,ship):
        out=[]
        out.append(0)
        if state.game.keys[pygame.K_a]:
            out[0]=-1
        elif state.game.keys[pygame.K_d]:
            out[0]=1
        out.append(0)
        if state.game.keys[pygame.K_w]:
            out[1]=-1
        elif state.game.keys[pygame.K_s]:
            out[1]=1
            
        mpos=pygame.mouse.get_pos()
        center=ship.rig.screenCenter()
        t=math.atan2(mpos[1]-center[1],mpos[0]-center[0])+math.pi/2
        t%=math.pi*2
        s=ship.speed[2]
        d=ship.data[7]
        a1=t-ship.rig.rot
        a2=((math.pi*2-ship.rig.rot)+t)
        a3=-1*(ship.rig.rot+(math.pi*2-t))
        proportionality=1000
        if math.fabs(a1)<math.fabs(a2) and math.fabs(a1)<math.fabs(a3):
            a=a1
        elif math.fabs(a2)<math.fabs(a1) and math.fabs(a2)<math.fabs(a3):
            a=a2
        else:
            a=a3

        r=0
        if False:#50/50 rotator
            #print(math.fabs(a)+0.2-((math.radians(ship.speed[2]**2)))/(2*math.radians(ship.data[6]+ship.data[7])))
            if math.fabs(a)+0.2<=((math.radians(ship.speed[2]**2)))/(2*math.radians(ship.data[6]+ship.data[7])):
                print("a")
                r=math.copysign(1,-1*a)
            else:
                print("b")
                r=math.copysign(1,a)
        else:
            r=(a/ship.data[6])*proportionality
            if r<-1:
                r=-1
            if r>1:
                r=1
        out.append(r)#rotation

        mstate=pygame.mouse.get_pressed()
        out.append(mstate[0])
        out.append(mstate[2])
        
        return out

class EvoAIInput:
    def __init__(self,copyFrom=None,mutationRate=2,mutationMagnitude=0.2):
        self.score=0
        self.lastRaycast=0
        self.lastEyes=None
        if copyFrom==None:
            self.hiddenSize=10
            self.numEyes=10
            self.inputSize=self.numEyes*2+5 #eyes*2+forwardspeed+sidespeed+angvel+health+constant
            self.outputSize=7 #see ship inputs
            self.rayLength=4000
            
            self.weights=[]
            for _ in range(self.hiddenSize*self.inputSize+self.hiddenSize*self.outputSize):
                self.weights.append(random.randint(-100,100)/100)
        else:
            self.hiddenSize=copyFrom.hiddenSize
            self.numEyes=copyFrom.numEyes
            self.inputSize=copyFrom.inputSize
            self.outputSize=copyFrom.outputSize
            self.rayLength=copyFrom.rayLength
            
            self.weights=[]
            for w in copyFrom.weights:
                if random.randint(1,mutationRate)==1:
                    w+=random.randint(-100,100)/100*mutationMagnitude
                self.weights.append(max(min(w, 1), -1))
    def getInputArray(self,deltaTime,state,ship):
        inputs=[]
        angSeparation=math.pi*2
        angSeparation/=self.numEyes
        eyeAng=ship.rig.rot
        eyepos=1
        if self.lastRaycast<=0:
            self.lastEyes=[]
        for i in range(self.numEyes):######Look through eyes
            if self.lastRaycast<=0:
                orayEnd=[self.rayLength,0]
                rayEnd=[0,0]
                rayEnd[0]=orayEnd[0]*math.cos(eyeAng)-orayEnd[1]*math.sin(eyeAng)
                rayEnd[1]=orayEnd[0]*math.sin(eyeAng)+orayEnd[1]*math.cos(eyeAng)
                rayEnd=[rayEnd[0]+ship.rig.x,rayEnd[1]+ship.rig.y]
                closestTarget=ship.world.radius*2
                for s in ship.world.shipList:#search ships
                    if s.team!=ship.team:
                        d=s.rig.raycast(((ship.rig.x,ship.rig.y),(rayEnd[0],rayEnd[1])))
                        if d!=None:
                            if d<closestTarget:
                                closestTarget=d
                inputs.append(self.rayLength-closestTarget)
                self.lastEyes.append(self.rayLength-closestTarget)
                closestTarget=ship.world.radius*2
                for obj in ship.world.tickQueue:#search projectiles
                    if isinstance(obj,wdcore.Projectile):
                        d=obj.rig.raycast(((ship.rig.x,ship.rig.y),(rayEnd[0],rayEnd[1])))
                        if d!=None:
                            if d<closestTarget:
                                closestTarget=d
                inputs.append(self.rayLength-closestTarget)
                self.lastEyes.append(self.rayLength-closestTarget)
            
            eyeAng+=angSeparation
        if self.lastRaycast>0:
            for i in range(self.numEyes*2):
                inputs.append(self.lastEyes[i])
        if self.lastRaycast<=0:
            self.lastRaycast=0#####raycast frame limiter
        self.lastRaycast-=1

        ###other inputs
        #forward and strafe
        i_angle=math.atan2(ship.speed[1],ship.speed[0])+math.pi/2
        i_angle=ship.rig.rot-i_angle
        i_xy=[0,0]
        i_xy[0]=ship.speed[0]*math.cos(i_angle)-ship.speed[1]*math.sin(i_angle)
        i_xy[1]=ship.speed[0]*math.sin(i_angle)+ship.speed[1]*math.cos(i_angle)
        inputs.append(i_xy[0])
        inputs.append(i_xy[1])
        #rotation
        inputs.append(ship.speed[2])
        #health
        inputs.append(ship.currentHealth/ship.data[0])
        #constant
        inputs.append(1)

        ####calculate network
        cw=0#current weight
        hidden=[]
        for _ in range(self.hiddenSize):
            h=0
            for i in range(self.inputSize):
                h+=inputs[i]*self.weights[cw]
                cw+=1
            h=math.tanh(h)
            hidden.append(h)
        outputs=[]
        for _ in range(self.outputSize):
            h=0
            for i in range(self.hiddenSize):
                h+=hidden[i]*self.weights[cw]
                cw+=1
            outputs.append(h)

        ##rotate movement
        newMovement=[0,0]
        newMovement[0]=outputs[0]*math.cos(-1*i_angle)-outputs[1]*math.sin(-1*i_angle)
        newMovement[1]=outputs[0]*math.sin(-1*i_angle)+outputs[1]*math.cos(-1*i_angle)
        outputs[0]=newMovement[0]
        outputs[1]=newMovement[1]
        for i in range(len(outputs)):#limit outputs with tanh
            outputs[i]=math.tanh(outputs[i])
        return outputs
                
        
        
