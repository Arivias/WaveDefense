import pygame
from pygame.locals import *
import time
import sys
import vecrig as vr
import math
import editor

class App:
    
    def __init__(self):
        #self.vec=vr.Rig("Resources/Vector_Rigs/Buttons/Button_Frame.json")#####
        #self.vec.x=400
        #self.vec.y=250
        #self.vec.scale=1
        ################
        
        self.running=True
        self.display_surf=None
        self.size=self.weight,self.height=960,540
        self.lastTime=time.time()
        pygame.font.init()
        self.editor=editor.Editor(self)
        self.display_surf=pygame.display.set_mode(self.size,pygame.HWSURFACE|pygame.DOUBLEBUF)#pygame.FULLSCREEN)

    def on_event(self,event):
        if event.type==pygame.QUIT:
            self.running=False

            
    def on_loop(self,evnt):
        self.display_surf.fill((0,0,0))
        #self.vec.rotateBy(0.4*self.deltaTime())
        #self.vec.render(self.display_surf)
        #event=pygame.event.get()
        self.editor.update_tick(self.display_surf,evnt)

    
    def on_render(self):
        pygame.display.update()

    
    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        while(self.running):
            evnt=pygame.event.get()
            for event in evnt:
                self.on_event(event)
            self.on_loop(evnt)
            self.on_render()
            self.lastTime=time.time()
        self.on_cleanup()

    def deltaTime(self):
        return (time.time()-self.lastTime)



if __name__=="__main__":
    app=App()
    app.on_execute()
