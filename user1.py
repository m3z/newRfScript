import simplejson as json
import command as cmd


#read json
f = open("2.json",'r')
jsonfile = ""
for line in f:
    jsonfile += line
f.close()
topology = json.loads(jsonfile)
#createSlice
controllerList = topology["usrInfo"]["controller"].keys()
for controller in controllerList:
    cmd.createSlice(topology["usrInfo"]["name"]+"_"+controller,\
                "tcp:"+topology["usrInfo"]["controller"][controller]\
                ,topology["usrInfo"]["email"])

#startOVS
OVSList = topology["nodes"].keys()
for OVS in OVSList:
    cmd.ovsOpenflowd(OVS,"127.0.0.1","6633")

#addFlowSpace
dpidList=cmd.getDpidList()
OVSNameDict=cmd.getOVSName(dpidList)
for OVS in OVSList:
    cmd.addFlowSpace(OVSNameDict[OVS],"20","all","Slice:"+\
                     topology["usrInfo"]["name"]+"_"+\
                     topology["nodes"][OVS]["attrs"]["controller"]+"=4")
#createlxc
lxcList = topology["vms"].keys()
for lxc in lxcList:
    cmd.createLxcDir(topology["usrInfo"]["name"]+"_"+lxc)
    vmInterfaceList=topology["vms"][lxc]["interface"].keys()
    vmInterfaceDict=topology["vms"][lxc]["interface"]
    cmd.createVmConfig(topology["usrInfo"]["name"]+"_"+lxc,vmInterfaceList)
    cmd.createFstab(topology["usrInfo"]["name"]+"_"+lxc)
    cmd.createVmInterface(topology["usrInfo"]["name"]+"_"+lxc,vmInterfaceList,vmInterfaceDict)
    
#startlxc
for lxc in lxcList:
    cmd.lxcStart(lxc)
#connect
for OVS in OVSList:
    interfaceList= topology["nodes"][OVS]["interface"].keys()
    for interface in interfaceList:
        cmd.ovsDpctl(OVS,topology["nodes"][OVS]["interface"][interface]["toward"])
