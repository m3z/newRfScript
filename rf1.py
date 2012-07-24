import simplejson as json
import command as cmd
import time

#read json
f = open("2.json",'r')
jsonfile = ""
for line in f:
    jsonfile += line
f.close()
topology = json.loads(jsonfile)

#create lxc

lxcList = topology["nodes"].keys()
address=101
for lxc in lxcList:
    cmd.createLxcDir(lxc)
    time.sleep(10)
    vmInterfaceList=topology["nodes"][lxc]["interface"].keys()
    vmInterfaceDict=topology["nodes"][lxc]["interface"]
    cmd.createVmConfig(lxc,vmInterfaceList,topology["usrInfo"]["name"])
    cmd.createFstab(lxc)
    cmd.createVmInterface(lxc,vmInterfaceList,vmInterfaceDict)
    address+=1
    cmd.createDaemons(lxc,topology["nodes"][lxc]["attrs"]["protocol"])
    if(topology["nodes"][lxc]["attrs"]["protocol"]="rip"):
        cmd.createRipd(lxc,vmInterfaceList,vmInterfaceDict)
    elif(topology["nodes"][lxc]["attrs"]["protocol"]="ospf"):
        ####
    else:
        ####

#start rf

cmd.startNox("switch","6363")
cmd.startNox("routeflowc","6666")
cmd.startRf()
for lxc in lxcList:
    lxcStart(lxc)
cmd.ovsOpenflowd('dp0', '127.0.0.1', 6666, 'rfovs')
cmd.ifconfig('dp0', 'up')
cmd.ovsOpenflowd('br0', '127.0.0.1', 6363)
cmd.ifconfig('br0', 'up', '192.168.1.1', '255.255.255.0')

for lxc in lxcList:
    vmInterfaceList=topology["nodes"][lxc]["interface"].keys()
    for vmInterface in vmInterfaceList:
        cmd.ovsDpctl("dp0",vmInterface)

for lxc in lxcList:
    cmd.ovsDpctl("br0",lxc+".0")


