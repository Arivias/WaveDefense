import pygame
from pygame.locals import *
import wavedefense
import time
import sys

class App:
    def __init__(self):
        self.game = wavedefense.Game()
        self.lastTime=time.time()
        self.deltaTime=0
        pygame.font.init()
        self.window=pygame.display.set_mode((960,540),pygame.HWSURFACE|pygame.DOUBLEBUF)

    def run(self):
        self.running=True
        while self.running:
            self.window.fill((0,0,0))
            event=pygame.event.get()
            self.deltaTime=time.time()-self.lastTime
            self.deltaTime=0.07
            self.lastTime=time.time()
            self.game.loop(self,event)
            self.game.render(self)
            pygame.display.update()
        pygame.quit()



if __name__=="__main__":
    app=App()
    app.run()
