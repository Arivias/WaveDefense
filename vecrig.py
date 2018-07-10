import json
import pygame
import math
from pygame.locals import *
from abc import ABC, abstractmethod


class RigPoint:
    def __init__(self,x,y,links,tags=[],color=(255,255,255),transparency=False):
        self.transparency=transparency
        self.color=color
        self.points=[x,y]
        self.rot_origin=[x,y]
        self.displacement=[0,0]
        self.links=links
        self.tags=tags
    def ptActual(self,x,y,scale,screenpos=[0,0],wscale=1.0):
        return [(scale*(self.points[0]+self.displacement[0])+x+(-1*screenpos[0]))*wscale,(scale*(self.points[1]+self.displacement[1])+y+(-1*screenpos[1]))*wscale]
    def applyScale(self,scale):
        points=[self.points[0],self.points[1]]
        points[0]*=scale
        points[1]*=scale
        return points


class Rig:
    def __init__(self,path,markers=False):
        self.markers=markers
        self.points=[]
        self.name="Unnamed"
        self.x=0
        self.y=0
        self.rot=0
        self.scale=1
        self.wscale=1.0
        self.screenpos=[0,0]
        self.colliderSegments=[]
        self.collisionRadius=0
        if path!=None:
            try:
                idata=json.loads(open(path).read())
                if "type" in idata.keys() and idata["type"]=="vecrig":
                    if idata["compat_version"]=="1.1":
                        self.name=idata["name"]
                        for pt in idata["points"]:
                            point=RigPoint(pt["x"],pt["y"],pt["links"],pt["tags"])
                            self.points.append(point)
                            #print(self.points[len(self.points)-1].ptsActual())
                        #print(self.name)
                        for pt in self.points:
                            if "collider" in pt.tags:
                                r=math.hypot(pt.points[0],pt.points[1])
                                self.collisionRadius=max(self.collisionRadius,r)
                                for lk in pt.links:
                                    if "collider" in self.points[lk].tags:
                                        alreadyDone=False
                                        for seg in self.colliderSegments:
                                            if pt in seg and self.points[lk] in seg:
                                                alreadyDone=True
                                                break
                                        if  not alreadyDone:
                                            self.colliderSegments.append([pt,self.points[lk]])
                    else:
                        print("WARNING: VecRig file \""+path+"\" is out of date and was not loaded.")
            except Exception:
                print("ERROR: Failed to load VectorRig \""+path+"\".")
        else:
            pass

    def render(self,window,color=None):
        #if self.collisionRadius>1:#show collisionRadius circles
        #    pygame.draw.circle(window,(0,255,255),(int(self.x),int(self.y)),int(self.collisionRadius),1)
        for pt in self.points:
            cl={}
            if self.markers:
                center=pt.ptActual(self.x,self.y,self.scale)
                pygame.draw.circle(window,(100,100,100),(int(center[0]),int(center[1])),3)
            transparency={}
            for lk in pt.links:
                if color==None:
                    cl[lk]=((pt.color[0]+self.points[lk].color[0])/2,(pt.color[1]+self.points[lk].color[1])/2,(pt.color[2]+self.points[lk].color[2])/2)
                else:
                    cl[lk]=color
                if pt.transparency or self.points[lk].transparency:
                    if self.ptOnScreen(pt.ptActual(self.x,self.y,self.scale,self.screenpos,self.wscale),window) or self.ptOnScreen(self.points[lk].ptActual(self.x,self.y,self.scale,self.screenpos,self.wscale),window):
                        transparency[lk]=True
                        #pta=pt.ptActual(self.x,self.y,self.scale)
                        #lka=self.points[lk].ptActual(self.x,self.y,self.scale)
                        #corner=[pta[0],pta[1]]
                        #if lka[0]<corner[0]:
                        #    corner[0]=lka[0]
                        #if lka[1]<corner[1]:
                        #    corner[1]=lka[1]
                        #copy=[pta[0],pta[1]]
                        #pta[0]-=lka[0]
                        #if pta[0]<0:
                        #    pta[0]=0
                        #pta[1]-=lka[1]
                        #if pta[1]<0:
                        #    pta[1]=0
                        #lka[0]-=copy[0]
                        #if pta[0]<0:
                        #    pta[0]=0
                        #lka[1]-=copy[1]
                        #if lka[1]<0:
                        #    lka[1]=0
                        #fabsx=math.fabs(pta[0]-lka[0])
                        #fabsy=math.fabs(pta[1]-lka[1])
                        #surf=pygame.Surface((fabsx+4,fabsy+4))
                        surf=pygame.Surface(window.get_size())
                        #pygame.draw.aaline(surf,cl[lk],(pta[0]+2,pta[1]+2),(lka[0]+2,lka[1]+2))#
                        pygame.draw.aaline(surf,cl[lk],pt.ptActual(self.x,self.y,self.scale,self.screenpos),self.points[lk].ptActual(self.x,self.y,self.scale,self.screenpos))
                        surf.set_colorkey((0,0,0))
                        #window.blit(surf,corner)
                        window.blit(surf,(0,0))
                else:
                    transparency[lk]=False
            for lk in pt.links:
                if transparency[lk]==False and (self.ptOnScreen(pt.ptActual(self.x,self.y,self.scale,self.screenpos,self.wscale),window) or self.ptOnScreen(self.points[lk].ptActual(self.x,self.y,self.scale,self.screenpos,self.wscale),window)):
                    pygame.draw.aaline(window,cl[lk],pt.ptActual(self.x,self.y,self.scale,self.screenpos,self.wscale),self.points[lk].ptActual(self.x,self.y,self.scale,self.screenpos,self.wscale))
        #pygame.draw.lines(window,(255,255,255),False,[(250,400),(700,250)],3)

    def rotateTo(self,rot):
        self.rot=rot%(2*math.pi)
        #print(str(self.points[1].points[0])+" * "+str(math.cos(rot))+" = "+ str(self.points[1].points[0]*math.cos(rot)))
        for pt in self.points:
            pt.points[0]=pt.rot_origin[0]*math.cos(rot)-pt.rot_origin[1]*math.sin(rot)
            pt.points[1]=pt.rot_origin[0]*math.sin(rot)+pt.rot_origin[1]*math.cos(rot)

    def rotateBy(self,rot):
        self.rotateTo(self.rot+rot)

    def toJson(self,name):
        jsn={}
        jsn["type"]="vecrig"
        jsn["compat_version"]="1.1"
        jsn["name"]=name
        pts=[]
        for pt in self.points:
            pos=pt.applyScale(self.scale)
            data={}
            data["x"]=pos[0]
            data["y"]=pos[1]
            data["links"]=[]
            for link in pt.links:
                data["links"].append(link)
            data["tags"]=pt.tags
            pts.append(data)
        jsn["points"]=pts
        return json.dumps(jsn)
    
    def deletePts(self,pts):
        for pt in pts:
            index=-1
            for p in range(len(self.points)):
                if pt==self.points[p]:
                    index=p
                    break
            if index!=-1:
                self.points.remove(pt)
                for p in self.points:
                    if index in p.links:
                        p.links.remove(index)
                    for link in range(len(p.links)):
                        if p.links[link]>index:
                            p.links[link]-=1
    def toLocalSpace(self,pos):#probably wont work with zoom
        return [-1*(self.x-pos[0])/self.scale,-1*(self.y-pos[1])/self.scale]
    def ptOnScreen(self,pos,window):
        size=window.get_size()
        return (pos[0]>=0 and pos[1]>=0 and pos[0]<size[0] and pos[1]<size[1])
    def screenCenter(self):
        return [(self.x+(-1*self.screenpos[0]))*self.wscale,(self.y+(-1*self.screenpos[1]))*self.wscale]

def orientation(p1,p2,p3):#https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    val=(p2[1]-p1[1])*(p3[0]-p2[0])-(p2[0]-p1[0])*(p3[1]-p2[1])
    if val==0:
        return 0
    elif val>0:
        return 1
    else:
        return 2
def onSegment(p,q,r):
    if q[0]<=max(p[0],r[0]) and q[0]>=min(p[0],r[0]) and q[1]<=max(p[1],r[1]) and q[1]>=min(p[1],r[1]):
        return True
    return False
def checkLineCollision(p1,q1,p2,q2):
    o1=orientation(p1,q1,p2)
    o2=orientation(p1,q1,q2)
    o3=orientation(p2,q2,p1)
    o4=orientation(p2,q2,q1)
    if o1!=o2 and o3!=o4:
        return True
    if o1==0 and onSegment(p1,p2,q1):
        return True
    if o2==0 and onSegment(p1,q2,q1):
        return True
    if o3==0 and onSegment(p2,p1,q2):
        return True
    if o4==0 and onSegment(p2,q1,q2):
        return True
    return False
        
class RigAnimator(ABC):
    def __init__(self,rig):
        self.rig=rig
        self.finished=False

    @abstractmethod
    def tick(self,deltaTime):
        pass
