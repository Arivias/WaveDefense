import pygame
from pygame.locals import *
import time
import sys
import vecrig

class App:
    
    def __init__(self):
        self.running=True
        self.display_surf=None
        self.size=self.weight,self.height=960,540
        self.lastTime=time.time()

    def on_init(self):
        pygame.init()
        self.display_surf=pygame.display.set_mode(self.size,pygame.HWSURFACE|pygame.DOUBLEBUF)#pygame.FULLSCREEN)
        pygame.display.toggle_fullscreen()
        self.running=True

    def on_event(self,event):
        if event.type==pygame.QUIT:
            self.running=False

            
    def on_loop(self):
        pygame.draw.lines(self.display_surf,(255,255,255),False,[(250,400),(700,250)],3)
        pass

    
    def on_render(self):
        
        pygame.display.update()

    
    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init()==False:
            self.running=False
        while(self.running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.lastTime=time.time()
        self.on_cleanup()

    def deltaTime(self):
        return (time.time()-self.lastTime)



if __name__=="__main__":
    app=App()
    app.on_execute()
