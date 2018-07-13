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
                proj=p_Simple(pt,self.ship,"bolt1.json",900,self.damage,(255,0,0),self.world)
                self.world.rigs.append(proj.rig)
                self.world.tickQueue.append(proj)
    def tick(self,deltaTime):
        if self.cooldown>0:
            self.cooldown=max(0,self.cooldown-deltaTime)


####projectiles

class p_Simple(wdcore.Projectile):
    def __init__(self,point,ship,path,speed,damage,color,world):
        super().__init__(world,ship.team,ship)
        self.speed=speed
        self.damage=damage
        self.rig=vecrig.Rig("Resources/Vector_Rigs/Projectiles/"+path)
        for pt in self.rig.points:
            pt.color=color
        self.rig.x=ship.rig.x+point.points[0]
        self.rig.y=ship.rig.y+point.points[1]
        self.rig.rotateTo(ship.rig.rot)
        self.closest=0
    def tick(self,deltaTime):
        if math.hypot(self.rig.x,self.rig.y)>self.world.radius:
            self.world.deleteQueue.append(self)
            self.world.deleteQueue.append(self.rig)
            if self.closest>0:
                self.rewardCreator(1/self.closest)
        self.rig.x+=self.speed*math.cos(self.rig.rot-math.pi/2)*deltaTime
        self.rig.y+=self.speed*math.sin(self.rig.rot-math.pi/2)*deltaTime
        for ship in self.world.shipList:
            if ship!=self.ship and ship.team!=self.ship.team:
                if self.rig.collidesWith(ship.rig):
                    self.world.deleteQueue.append(self.rig)
                    self.world.deleteQueue.append(self)
                    ship.damage(self.damage)
                    self.rewardCreator(self.damage)
                else:
                    d=math.hypot(self.rig.x-ship.rig.x,self.rig.y-ship.rig.y)
                    if d<self.closest or self.closest==0:
                        self.closest=d
                
        
