import vecrig
import math
import wdcore


####weapons

class wp_PulseLaser(wdcore.Weapon):
    def __init__(self,ship,damage,category,world):
        super().__init__("Autopulse Mk 1",ship,category,world)
        self.damage=damage
        self.cooldown=0
    def fire(self):
        if self.cooldown==0:
            self.cooldown=0.5
            for pt in self.wpoints:
                proj=p_Simple(pt,self.ship,"bolt1.json",900,self.damage,(255,0,0))
                self.world.rigs.append(proj.rig)
                self.world.tickQueue.append(proj)
    def tick(self,deltaTime):
        if self.cooldown>0:
            self.cooldown=max(0,self.cooldown-deltaTime)


####projectiles

class p_Simple(wdcore.Projectile):
    def __init__(self,point,ship,path,speed,damage,color):
        super().__init__()
        self.speed=speed
        self.damage=damage
        self.rig=vecrig.Rig("Resources/Vector_Rigs/Projectiles/"+path)
        for pt in self.rig.points:
            pt.color=color
        self.rig.x=ship.rig.x+point.points[0]
        self.rig.y=ship.rig.y+point.points[1]
        self.rig.rotateTo(ship.rig.rot)
        self.ship=ship
    def tick(self,deltaTime):
        self.rig.x+=self.speed*math.cos(self.rig.rot-math.pi/2)*deltaTime
        self.rig.y+=self.speed*math.sin(self.rig.rot-math.pi/2)*deltaTime
        
