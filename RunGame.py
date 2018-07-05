import pygame
from pygame.locals import *
import time
import sys

class App:
    def __init__(self):
        self.lastTime=time.time()
        pygame.font.init()
        self.window=pygame.display.set_mode((960,540),pygame.HWSURFACE|pygame.DOUBLEBUF)

    def run(self):
        self.running=False
        while self.running:
            event=pygame.event.get()
            self.lastTime=time.time()
            #main loop
            #render loop
        pygame.quit()

    def deltaTime(self):
        return (time.time()-self.lastTime)



if __name__=="__main__":
    app=App()
    app.run()
