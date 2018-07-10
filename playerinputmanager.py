import pygame
from pygame.locals import *
import math


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
        a3=ship.rig.rot+(math.pi*2-t)
        proportionality=1000
        if math.fabs(a1)<math.fabs(a2) and math.fabs(a1)<math.fabs(a3):
            r=(a1/ship.data[6])*proportionality
        elif math.fabs(a2)<math.fabs(a1) and math.fabs(a2)<math.fabs(a3):
            r=(ship.data[6]/a2)*proportionality
        else:
            r=-1*(ship.data[6]/a3)*proportionality
        if r<-1:
            r=-1
        if r>1:
            r=1
        out.append(r)#put output here
        
        return out
