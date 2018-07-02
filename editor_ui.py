import editor as e

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
    row.append(e.Button(editor,rp+"rotate.json","rotate","panemode","e"))
    row.append(e.Button(editor,rp+"scale.json","scale","panemode","r"))
    b.append(row)
    row=[]
    row.append(e.Button(editor,rp+"undo.json","undo","func","z",lambda c,x:0))
    row.append(e.Button(editor,rp+"mirror.json","mirror","panemode","m",lambda c,x:mirrorpane(editor,x)))
    b.append(row)
    row=[]
    row.append(e.Button(editor,rp+"selectall.json","selectall","func","a",lambda c,x:editor.selectall()))
    row.append(e.Button(editor,rp+"deselect.json","deselect","func","d",lambda c,x:editor.deselect()))
    row.append(e.Button(editor,rp+"file.json","file","panemode","s",lambda c,x:filepane(editor,x)))
    b.append(row)

    row=[]
    row.append(e.TextBox(editor,"scale",func=lambda c,x:scale(editor,x),contents="1"))
    b.append(row)
    return e.EditorPane("main",b)
def filepane(editor,x):
    if x==1:
        b=[]
        rp="Resources/Vector_Rigs/Buttons/"
        row=[e.TextBox(editor,"filename")]
        b.append(row)
        row=[]
        row.append(e.Button(editor,rp+"save.json","save","func",function=lambda c,x:save(editor,x)))
        
        row.append(e.Button(editor,rp+"load.json","load","func"))
        b.append(row)
        editor.stackPane(e.EditorPane("file",b))
    elif x==0:
        editor.unstackPane("file")
def save(editor,x):
    if x==1:
        editor.save()
        editor.panes[0].objnames["file"].unclick()
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
        row.append(e.Button(editor,"mirrorx.json","mirrorx","toggle",function=lambda c,x:setmirror(editor,0,x,c),value=v))
        v=1
        if editor.mirrormode[1]==False:
            v=0
        row.append(e.Button(editor,"mirrory.json","mirrory","toggle",function=lambda c,x:setmirror(editor,1,x,c),value=v))
        b.append(row)
        editor.stackPane(e.EditorPane("mirror",b))
    else:
        editor.unstackPane("mirror")
def setmirror(editor,n,x,c):
    if not c:
        return
    editor.mirrormode[n]= x==1
