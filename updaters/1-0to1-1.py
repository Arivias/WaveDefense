import json
while True:
    i=input()+".json"
    j=json.loads(open(i,"r").read())
    j["compat_version"]="1.1"
    for pt in j["points"]:
        pt["tags"]=[]
    print(json.dumps(j),file=open(i,"w"))
