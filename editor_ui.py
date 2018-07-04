import editor as e
import vecrig as vr

def mainpane(editor):
    b=[]
    rp="Resources/Vector_Rigs/Buttons/"

    row=[]
    row.append(e.Button(editor,rp+"pointer.json","pointer","panemode","q"))
    row.append(e.Button(editor,rp+"linker.json","linker","panemode","l"))
    row.append(e.Button(editor,rp+"delete.json","delete","func","x",lambda c,x:editor.deleteSelection()))
    b.append(row)
    row=[]
    row.append(e.Button(editor,rp+"translate.json","translate","panemode","w"))
    row.append(e.Button(editor,rp+"rotate.json","rotate","panemode","e",lambda c,x:unset_selection_single(editor,c)))
    row.append(e.Button(editor,rp+"scale.json","scale","panemode","r",lambda c,x:unset_selection_single(editor,c)))
    b.append(row)
    row=[]
    row.append(e.Button(editor,rp+"mirror.json","mirror","panemode","m",lambda c,x:mirrorpane(editor,x)))
    row.append(e.Button(editor,rp+"clone.json","clone","func","c",lambda c,x:clone(c,x,editor)))
    row.append(e.Button(editor,rp+"bg.json","bg","panemode","b",lambda c,x:bgpane(editor,c)))
    b.append(row)
    row=[]
    row.append(e.Button(editor,rp+"selectall.json","selectall","func","a",lambda c,x:editor.selectall()))
    row.append(e.Button(editor,rp+"deselect.json","deselect","func","d",lambda c,x:editor.deselect()))
    row.append(e.Button(editor,rp+"file.json","file","panemode","s",lambda c,x:filepane(editor,x)))
    b.append(row)

    row=[]
    row.append(e.TextBox(editor,"scale",func=lambda x:scale(editor,x),contents="1"))
    b.append(row)
    return e.EditorPane("main",b)
def filepane(editor,x):
    if x==1:
        b=[]
        rp="Resources/Vector_Rigs/Buttons/"
        row=[e.TextBox(editor,"filename",func=lambda x:setname(editor,x),contents=editor.rig.name)]
        b.append(row)
        row=[]
        row.append(e.Button(editor,rp+"save.json","save","func",function=lambda c,x:save(editor,x)))
        
        row.append(e.Button(editor,rp+"file.json","load","func",function=lambda c,x:load(editor,c)))
        b.append(row)
        editor.stackPane(e.EditorPane("file",b))
    elif x==0:
        editor.unstackPane("file")
def setname(editor,x):
    editor.rig.name=x
def save(editor,x):
    if x==1:
        editor.save()
        editor.panes[0].objnames["file"].unclick()
def load(editor,c):
    if c:
        if editor.loadRig(editor.findpanename("file").objnames["filename"].contents):
            editor.unstackPane("file")
def scale(editor,x):
    try:
        editor.rig.scale=float(x)
    except:
        editor.panes[0].objnames["scale"].contents="1"
def mirrorpane(editor,x):
    if x==1:
        b=[]
        rp="Resources/Vector_Rigs/Buttons/"
        row=[]
        v=1
        if editor.mirrormode[0]==False:
            v=0
        row.append(e.Button(editor,rp+"mirrorx.json","mirrorx","toggle",",",function=lambda c,x:setmirror(editor,0,x,c),value=v))
        v=1
        if editor.mirrormode[1]==False:
            v=0
        row.append(e.Button(editor,rp+"mirrory.json","mirrory","toggle",".",function=lambda c,x:setmirror(editor,1,x,c),value=v))
        b.append(row)
        editor.stackPane(e.EditorPane("mirror",b))
    else:
        editor.unstackPane("mirror")
def setmirror(editor,n,x,c):
    if not c:
        return
    editor.mirrormode[n]= x==1
def clone(c,x,editor):
    if c:
        new=[]
        for pt in editor.selection:
            new.append(vr.RigPoint(pt.points[0],pt.points[1],[]))
        editor.rig.points+=new
        editor.selection=new
def unset_selection_single(editor,c):
    if not c:
        editor.selection_single=None
def bgpane(editor,c):
    if c:
        rp="Resources/Vector_Rigs/Buttons/"
        b=[]
        b.append([e.TextBox(editor,"bgfile")])
        row=[]
        row.append(e.Button(editor,rp+"file.json","loadbg","func",function=lambda c,x:setbg(editor,c)))
        v=1
        if not editor.bgshow:
            v=0
        row.append(e.Button(editor,rp+"toggle.json","toggle","toggle",function=lambda c,x:editor.togglebg(c),value=v))
        row.append(e.Button(editor,rp+"delete.json","delbg","func",function=lambda c,x:delbg(editor,c)))
        b.append(row)
        b.append([e.TextBox(editor,"bgscale",contents=str(editor.bgscale),func=lambda x:editor.setbgscale(x))])
        editor.stackPane(e.EditorPane("bg",b))
    else:
        editor.unstackPane("bg")
def setbg(editor,c):
    if c:
        editor.setbg()
def delbg(editor,c):
    if c:
       editor.bgimage=None

