import math
import vecrig as vr
import json
import pygame
from pygame.locals import *
from abc import ABC, abstractmethod
import time
import editor_ui

class EditorPane:
    def __init__(self,name,objects):
        self.name=name
        self.objnames={}
        self.mode=""
        self.objects=objects
        for row in self.objects:
            for obj in row:
                self.objnames[obj.name]=obj
        
        longest=0
        for i in self.objects:
            if self.rsize(i)>longest:
                longest=self.rsize(i)
        self.xwidth=longest*(40+4)#2 pix on each side
        self.xwidth-=20
        self.xborder=self.xwidth+22
        self.yborder=len(objects)*44
        self.ystart=0
    def setPrevious(self,prev):
        self.ystart=0
        if prev!=None:
            self.ystart=prev.ystart+prev.yborder+4
    def draw(self,window):
        xpos=window.get_size()[0]-(self.xwidth+5)
        #draw bg
        pygame.draw.rect(window,(50,50,50),[window.get_size()[0]-(self.xborder+6),self.ystart+2,window.get_size()[0]-20,self.yborder+2])
        pygame.draw.rect(window,(255,255,255),[window.get_size()[0]-(self.xborder+6),self.ystart+2,window.get_size()[0]-2,self.yborder+2],1)
        #draw paneobjects
        xp=xpos
        ypos=-20+self.ystart
        for row in self.objects:
            ypos+=44
            xpos=xp
            for ry in row:
                ry.draw(xpos,ypos,window)
                xpos+=44*ry.width
    def posInPane(self,window,x,y):
        size=window.get_size()
        if x>size[0]-self.xborder and y>self.ystart and y<self.ystart+self.yborder:
            return True
        return False
    def unclickByObjClaimType(self,obj):
        if obj.claimtype=="func" or obj.claimtype=="toggle":
            return
        for r1 in self.objects:
            for ob in r1:
                if ob!=obj and ob.claimtype==obj.claimtype:
                    mode=ob.unclick()
                    if mode!="func":
                        self.mode=mode
    def clickObj(self,x,y):
        for row in self.objects:
            for obj in row:
                if obj.posInObj(x,y) and (obj.value==0 or obj.claimtype=="toggle"):
                    self.unclickByObjClaimType(obj)
                    mode=obj.click()
                    if mode!="func":
                        self.mode=mode
                    return True
        return False
    def hotkey(self,x):
        for row in self.objects:
            for obj in row:
                if obj.hotkey!="" and obj.hotkey==x and obj.value==0:
                    self.unclickByObjClaimType(obj)
                    mode=obj.click()
                    if mode!="func":
                        self.mode=mode
                    return True
        return False
    def rsize(self,row):
        out=0
        for obj in row:
            out+=obj.width
        return out

class PaneObject(ABC):
    def __init__(self,editor,height,width,name,claim,hotkey,value=0):
        self.editor=editor
        self.hotkey=hotkey
        self.claimtype=claim
        self.x=0
        self.y=0
        self.name=name
        self.value=value
        self.height=height
        self.width=width

    @abstractmethod
    def draw(self,x,y,window):
        pass
    @abstractmethod
    def posInObj(self,x,y):
        pass
    @abstractmethod
    def click(self):
        pass
    @abstractmethod
    def unclick(self):
        pass

class Button(PaneObject):
    def __init__(self,editor,img,name,claim,hotkey='',function=None,value=0):
        super().__init__(editor,1,1,name,claim,hotkey,value)
        self.imgBox=vr.Rig("Resources/Vector_Rigs/Buttons/Button_Frame.json")
        self.function=function
        self.img=vr.Rig(img)
    
    def draw(self,x,y,window):
        self.x=x
        self.y=y
        linecolor=(255,255,255)
        bgcolor=(20,20,20)
        if self.value==1 and self.claimtype!="func":
            linecolor=(0,255,255)
            bgcolor=(75,75,75)
        pygame.draw.rect(window,bgcolor,[x-20,y-20,40,40])
        self.img.x=x
        self.img.y=y
        self.img.render(window,linecolor)
        self.imgBox.x=x
        self.imgBox.y=y
        self.imgBox.render(window,linecolor)
    def posInObj(self,x,y):
        return x>self.x-20 and x<self.x+20 and y>self.y-20 and y<self.y+20
    def click(self):
        if self.claimtype=="toggle":
            if self.value==1:
                self.value=0
            else:
                self.value=1
        else:
            self.value=1
        if self.function!=None:
            self.function(True,self.value)
        if self.claimtype=="func":
            self.value=0
            return "func"
        return self.name
    def unclick(self):
        self.value=0
        if self.function!=None:
            self.function(False,self.value)
        return ""

class TextBox(PaneObject):
    def __init__(self,editor,name,hotkey="",func=lambda x:0,contents="",font="Arial",fontsize=20):
        super().__init__(editor,1,3,name,"panemode",hotkey)
        self.func=func
        self.font=pygame.font.SysFont(font,fontsize)
        self.contents=contents
        self.x=0
        self.y=0
        self.active=False
        self.previous_handler=None
    def draw(self,x,y,window):
        self.x=x
        self.y=y
        linecolor=(255,255,255)
        bgcolor=(20,20,20)
        if self.active:
            linecolor=(0,255,255)
            bgcolor=(75,75,75)
        pygame.draw.rect(window,bgcolor,[x-20,y-20,40+(self.width-1)*44,40])
        pygame.draw.rect(window,linecolor,[x-20,y-20,40+(self.width-1)*44,40],1)
        txtsurf=self.font.render(self.contents,True,linecolor)
        window.blit(txtsurf,(x-17,y-10))
    def posInObj(self,x,y):
        return x>self.x-20 and x<self.x+20+44*(self.width-1) and y>self.y-20 and y<self.y+20
    def handler(self,x):
        if x.key==pygame.K_BACKSPACE:
            if len(self.contents)>0:
                self.contents=self.contents[:len(self.contents)-1]
        elif x.key==pygame.K_RETURN:
            self.func(self.contents)
            self.unclick()
        else:
            self.contents+=x.unicode
    def click(self):
        #self.contents=""
        self.previous_handler=self.editor.keylistener
        self.editor.keylistener=lambda x:self.handler(x)
        self.active=True
        return ""
    def unclick(self):
        if self.active:
            self.editor.keylistener=self.previous_handler
        self.active=False
        return ""
        

class Editor:
    def __init__(self,app):
        self.keys={}
        self.keys[pygame.K_LSHIFT]=False
        self.keys[pygame.K_LCTRL]=False
        self.centerpos=None
        self.selection=[]
        self.rig = vr.Rig(None,True)
        self.app=app
        self.last_mouse=(0,0,0)
        self.mm="none"
        self.mousemode=-1
        self.clicktime=0
        self.panes=[]
        self.func_list=[]
        self.mirrormode=[False,False]
        #self.func_list2=[]
        self.keylistener = lambda x:self.listener_hotkey(x)
        self.upkeylistener = lambda x:self.listener_upkey(x)
        
        #r1=[Button("Resources/Vector_Rigs/1.json","pointer","panemode"),Button("Resources/Vector_Rigs/1.json","pointer2","panemode")]
        #r2=r1+r1
        #self.panes.append(EditorPane([r1,r2]))
        #self.panes.append(EditorPane([r1,r2,r2,r2,r1,r1]))
        #self.panes[1].setPrevious(self.panes[0])

        self.panes.append(editor_ui.mainpane(self))

    def listener_hotkey(self,x):
        if x.key==pygame.K_LSHIFT:
            self.keys[pygame.K_LSHIFT]=True
        elif x.key==pygame.K_LCTRL:
            self.keys[pygame.K_LCTRL]=True
        for pane in self.panes:
            if pane.hotkey(x.unicode):
                break
    def listener_upkey(self,x):
        if x.key==pygame.K_LSHIFT:
            self.keys[pygame.K_LSHIFT]=False
        elif x.key==pygame.K_LCTRL:
            self.keys[pygame.K_LCTRL]=False

    def update_tick(self,window,evnt):#############################
        mstate=pygame.mouse.get_pressed()
        mpos=pygame.mouse.get_pos()
        if mstate[0]==1 or mstate[2]==1:
            if self.last_mouse[0]==0:
                self.clicktime=time.time()
            if self.mm=="none":
                for ep in self.panes:
                    if ep.posInPane(window,mpos[0],mpos[1]):
                        self.mm="epane"
                if self.mm=="none":
                    self.mm=self.panes[0].mode
                #######Run on first click
                if self.mm=="pointer" and mstate[0]==1:
                    pass
                elif self.mm=="linker":
                    if mstate[0]==1:
                        self.mousemode=0
                        self.func_list=[None]
                        self.selection=[self.nearest_point(mpos[0],mpos[1],[])]
                    else:
                        self.mousemode=2
                        self.func_list=[0,0]
            ###run on tick
            if self.mm=="pointer" and mstate[0]==1:
                if self.last_mouse[0]==0:
                    self.func_list=[mpos,False,self.keys[pygame.K_LSHIFT],[]]
                if math.sqrt(math.pow(math.fabs(self.func_list[0][0]-mpos[0]),2)+math.pow(math.fabs(self.func_list[0][1]-mpos[1]),2))>10:
                    self.func_list[1]=True
                    x1=self.func_list[0][0]
                    x2=mpos[0]
                    y1=self.func_list[0][1]
                    y2=mpos[1]
                    if x1>x2:
                        t=x1
                        x1=x2
                        x2=t
                    if y1>y2:
                        t=y1
                        y1=y2
                        y2=t
                    self.func_list[3]=[]
                    for pt in self.rig.points:
                        pts=pt.ptActual(self.rig.x,self.rig.y,self.rig.scale)
                        if pts[0]>x1 and pts[0]<x2 and pts[1]>y1 and pts[1]<y2:
                            self.func_list[3].append(pt)
                            
                else:
                    self.func_list[1]=False
                    
            elif self.mm=="linker":
                if self.mousemode==0:
                    pt=self.nearest_point(mpos[0],mpos[1],self.selection)
                    if pt !=None and pt!=self.func_list[0]:
                        if self.func_list[0]==None:
                            self.link(self.selection[0],pt,True)
                        else:
                            self.link(self.selection[0],self.func_list[0],True)
                            self.link(self.selection[0],pt,True)
                        self.func_list=[pt]
                else:
                    if self.keys[pygame.K_LCTRL]:
                        tx=0
                        ty=0
                        ndx=-1
                        ndy=-1
                        for pt in self.rig.points:
                            pos=pt.ptActual(self.rig.x,self.rig.y,self.rig.scale)
                            x=math.fabs(pos[0]-mpos[0])
                            y=math.fabs(pos[1]-mpos[1])
                            if x<30 and (ndx==-1 or x<ndx):
                                ndx=x
                                tx=pos[0]
                            if y<30 and (ndy==-1 or y<ndy):
                                ndy=y
                                ty=pos[1]
                        pos=[self.rig.x,self.rig.y]
                        x=math.fabs(pos[0]-mpos[0])
                        y=math.fabs(pos[1]-mpos[1])
                        if x<30 and (ndx==-1 or x<ndx):
                            ndx=x
                            tx=pos[0]
                        if y<30 and (ndy==-1 or y<ndy):
                            ndy=y
                            ty=pos[1]
                        ppos=[mpos[0],mpos[1]]
                        if ndx!=-1 and (ndx<ndy or self.keys[pygame.K_LSHIFT]==False):
                            ppos[0]=tx
                        if ndy!=-1 and (ndy<ndx or self.keys[pygame.K_LSHIFT]==False):
                            ppos[1]=ty
                        self.func_list=ppos
                    

        if mstate[0]==0 and self.last_mouse[0]==1:#Mouse 1 Release
            if self.mm=="epane":
                for pane in self.panes:
                    if pane.clickObj(mpos[0],mpos[1]):
                        break
            elif self.mm=="pointer":
                if self.func_list[1]:
                    if self.func_list[2]:
                        self.selection+=self.func_list[3]
                    else:
                        self.selection=self.func_list[3]
                else:
                    if self.keys[pygame.K_LSHIFT]:
                        self.selection.append(self.nearest_point(mpos[0],mpos[1],[]))
                    else:
                        self.selection=[self.nearest_point(mpos[0],mpos[1],[])]
            elif self.mm=="linker":
                self.mousemode=-1
        if mstate[2]==0 and self.last_mouse[2]==1:#Mouse 2 Release
            if self.mm=="epane":
                pass
            elif self.mm=="pointer":
                pass
            elif self.mm=="linker":
                if self.centerpos!=None:
                    pos=(0,0)
                    if self.keys[pygame.K_LCTRL]:
                        pos=(-1*(self.centerpos[0]-self.func_list[0]),-1*(self.centerpos[1]-self.func_list[1]))
                    else:
                        pos=(-1*(self.centerpos[0]-mpos[0]),-1*(self.centerpos[1]-mpos[1]))
                    self.rig.points.append(vr.RigPoint(pos[0]/self.rig.scale,pos[1]/self.rig.scale,[]))
                
        if mstate[0]==0 and mstate[2]==0:######Run after all mouse stuff
            self.mm="none"
        self.last_mouse=mstate

        for ev in evnt:
            if ev.type==2:#2 is down, 3 is up
                self.keylistener(ev)
            elif ev.type==3:
                self.upkeylistener(ev)

        #draw stuff
        xtarget=0
        for pane in self.panes:
            pane.draw(window)
            if xtarget<pane.xwidth:
                xtarget=pane.xwidth
        size=window.get_size()
        xtarget+=24
        xtarget=size[0]-xtarget
        self.centerpos=(xtarget/2,size[1]/2)
        self.rig.x=self.centerpos[0]
        self.rig.y=self.centerpos[1]
        #grid
        gridcolor=(50,50,50)
        pygame.draw.aaline(window,gridcolor,(0,size[1]/2),(xtarget,size[1]/2))
        pygame.draw.aaline(window,gridcolor,(xtarget/2,0),(xtarget/2,size[1]))
        pygame.draw.rect(window,gridcolor,[self.centerpos[0]-20,self.centerpos[1]-20,40,40],1)
        pygame.draw.rect(window,gridcolor,[self.centerpos[0]-120,self.centerpos[1]-120,240,240],1)
        
        #precise placement lines
        if self.panes[0].objnames["linker"].value==1 and self.keys[pygame.K_LCTRL]:
            for pt in self.rig.points:
                precisecolor=(35,35,35)
                pos=pt.ptActual(self.rig.x,self.rig.y,self.rig.scale)
                pygame.draw.aaline(window,precisecolor,(0,pos[1]),(xtarget,pos[1]))
                pygame.draw.aaline(window,precisecolor,(pos[0],0),(pos[0],size[1]))

        self.rig.render(window)
        
        for pt in self.selection:
            if pt!=None:
                center=pt.ptActual(self.rig.x,self.rig.y,self.rig.scale)
                pygame.draw.circle(window,(175,175,175),(int(center[0]),int(center[1])),5,1)
        if self.mm=="pointer" and mstate[0]==1:
            if self.func_list[1]:
                for pt in self.func_list[3]:
                    center=pt.ptActual(self.rig.x,self.rig.y,self.rig.scale)
                    pygame.draw.circle(window,(175,175,175),(int(center[0]),int(center[1])),5,1)
            if self.func_list[1]:
                pygame.draw.rect(window,(0,255,255),[self.func_list[0][0],self.func_list[0][1],-1*(self.func_list[0][0]-mpos[0]),-1*(self.func_list[0][1]-mpos[1])],1)
        

    def nearest_point(self,x,y,exclude):
        nearest=None
        nd=0
        for pt in self.rig.points:
            if not pt in exclude:
                if nearest==None:
                    nearest=pt
                    pos=pt.ptActual(self.rig.x,self.rig.y,self.rig.scale)
                    nd=(math.pow(math.fabs(pos[0]-x),2)+math.pow(math.fabs(pos[1]-y),2))
                else:
                    pos=pt.ptActual(self.rig.x,self.rig.y,self.rig.scale)
                    d=(math.pow(math.fabs(pos[0]-x),2)+math.pow(math.fabs(pos[1]-y),2))
                    if d<nd:
                        nd=d
                        nearest=pt
        return nearest
    def deselect(self):
        self.selection=[]
    def ptindex(self,pt):
        for i in range(len(self.rig.points)):
            if self.rig.points[i]==pt:
                return i
        return -1
    def link(self,p1,p2,unlink=False):
        if p1==None or p2==None:
            return
        index=self.ptindex(p1)
        index2=self.ptindex(p2)
        for ln in p1.links:
            if ln==index2:
                if unlink:
                    p1.links.remove(index2)
                return
        for ln in p2.links:
            if ln==index:
                if unlink:
                    p2.links.remove(index)
                return
        p1.links.append(index2)
    def unstackPane(self,name):
        for pane in self.panes:
            if pane.name==name:
                for row in pane.objects:
                    for obj in row:
                        obj.unclick()
                self.panes.remove(pane)
                break
        last=None
        for pane in self.panes:
            pane.setPrevious(last)
            last=pane
    def stackPane(self,pane):
        pane.setPrevious(self.panes[len(self.panes)-1])
        self.panes.append(pane)
    def save(self):
        name=self.findpanename("file").objnames["filename"].contents
        print(self.rig.toJson(name),file=open(name+".json","w"))
    def findpanename(self,name):
        for pane in self.panes:
            if pane.name==name:
                return pane
        return None
    def selectall(self):
        self.selection=[]
        for pt in self.rig.points:
            self.selection.append(pt)
    def deleteSelection(self):
        self.rig.deletePts(self.selection)
        self.selection=[]
        
