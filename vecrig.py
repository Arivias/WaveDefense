import json
import pygame
import math
from pygame.locals import *
from abc import ABC, abstractmethod


class RigPoint:
    def __init__(self,x,y,links):
        self.color=(255,255,255,255)
        self.points=[x,y]
        self.rot_origin=[x,y]
        self.displacement=[0,0]
        self.links=links
    def ptActual(self,x,y,scale):
        return [scale*(self.points[0]+self.displacement[0])+x,scale*(self.points[1]+self.displacement[1])+y]
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
        if path!=None:
            try:
                idata=json.loads(open(path).read())
                if "type" in idata.keys() and idata["type"]=="vecrig":
                    if idata["compat_version"]=="1.0":
                        self.name=idata["name"]
                        for pt in idata["points"]:
                            point=RigPoint(pt["x"],pt["y"],pt["links"])
                            self.points.append(point)
                            #print(self.points[len(self.points)-1].ptsActual())
                        #print(self.name)
                    else:
                        print("WARNING: VecRig file \""+path+"\" is out of date and was not loaded.")
            except Exception:
                print("ERROR: Failed to load VectorRig \""+path+"\".")
        else:
            pass

    def render(self,window,color=(255,255,255),forceColor=False):
        for pt in self.points:
            cl=color
            if not forceColor:
                cl=pt.color
            if self.markers:
                center=pt.ptActual(self.x,self.y,self.scale)
                pygame.draw.circle(window,(100,100,100),(int(center[0]),int(center[1])),3)
            transparency=[]
            draw=[]
            wsize=window.get_size()
            for lk in pt.links:
                alpha=pt.color+self.points[lk]
                alpha/=2
                if alpha==255:
                    transparency+=True
                    
                else:
                    transparency+=False
                if pt
            for lk in pt.links:
                pygame.draw.aaline(window,color,pt.ptActual(self.x,self.y,self.scale),self.points[lk].ptActual(self.x,self.y,self.scale))
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
        jsn["compat_version"]="1.0"
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
    def toLocalSpace(self,pos):
        return [-1*(self.x-pos[0])/self.scale,-1*(self.y-pos[1])/self.scale]
    def ptOnScreen(self,pos,window):
        return 
        
class RigAnimator(ABC):
    def __init__(self,rig):
        self.rig=rig
        self.finished=False

    @abstractmethod
    def tick(self,deltaTime):
        pass
