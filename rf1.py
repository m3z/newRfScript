import simplejson as json
import command as cmd
import time
import sys
#read json
filename=sys.argv[1]
f = open(filename,'r')
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
    cmd.createRfConfig(lxc,vmInterfaceList)
    cmd.createFstab(lxc)
    cmd.createRfInterface(lxc,vmInterfaceList,vmInterfaceDict,address)
    address+=1
    cmd.createDaemons(lxc,topology["nodes"][lxc]["attrs"]["protocol"])
    if(topology["nodes"][lxc]["attrs"]["protocol"]=="rip"):
        cmd.createRipd(lxc,vmInterfaceList,vmInterfaceDict)
    #elif(topology["nodes"][lxc]["attrs"]["protocol"]=="ospf"):
 

#start rf

cmd.startNox("switch","6363")
cmd.startNox("routeflowc","6666")
cmd.startRf()
for lxc in lxcList:
    cmd.lxcStart(lxc)
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


