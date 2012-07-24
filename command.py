# -*- coding: utf-8 -*-
import os
import re


def ovsOpenflowd(name, ip, port, hw_desc = None):
    if(hw_desc):
        cmdString = '''ovs-openflowd --hw-desc='''+ hw_desc + \
                    ' ' + name +'  tcp:' + ip + ':' + str(port) + \
                    ''' --out-of-band --detach'''
    else:
        cmdString = '''ovs-openflowd ''' + name + ' tcp:' + \
                    ip + ':' + str(port) + \
                    ''' --out-of-band --detach'''
    
    os.system(cmdString)
    print cmdString

def ovsDpctl(entity, interface, action = 'add-if'):
    cmdString = 'ovs-dpctl ' + action + ' ' + entity + \
                ' ' + interface
    os.system(cmdString)
    print cmdString

def lxcStart(name):
    cmdString = '''lxc-start -n ''' + name + ''' -d''';
    os.system(cmdString)
    print cmdString


#启动flowvisor
def runFlowVisor():
        cmdString = "/usr/local/sbin/flowvisor /usr/local/etc/flowvisor/flowvisor-config.xml &"
        os.system(cmdString)
        print cmdString

#删除指定slice
def delSlices(slicename):
        cmdString = 'fvctl --passwd-file=/root/.fvp deleteSlice ' + slicename
        os.system(cmdString)
        print cmdString

#删除所有slice
def cleanSlices():
        cmdString = "fvctl --passwd-file=/root/.fvp listSlices"
        sList = os.popen(cmdString).readlines()
        for sli in sList:
                sli = re.split(': ',sli)[1].rstrip()
                if(sli!='fvadmin' and sli!=None):
                        delSlices(sli)
                        #cmdString = "fvctl --passwd-file=/root/.fvp deleteSlice " + sli
                        #os.system(cmdString)
                        #print cmdString

#删除flowspace指定项
def delFlowSpace(flowspaceID):
        cmdString = "fvctl --passwd-file=/root/.fvp removeFlowSpace "+ flowspaceID
        os.system(cmdString)
        print cmdString
#清空flowspace
def cleanFlowSpace():
        cmdString = "fvctl --passwd-file=/root/.fvp listFlowSpace"
        fList = os.popen(cmdString).readlines()
        for flowspace in fList:
                flowspace = re.search('(?<=id=\[)\d+',flowspace)
                if(flowspace):
                        delFlowSpace(flowspace.group())

#创建slice
def createSlice(slicename,controller,email):
        cmdString = "fvctl --passwd-file=/root/.fvp createSlice " + slicename + ' ' + controller + ' ' + email
        os.system(cmdString)
        print cmdString

#增加flowspace项
def addFlowSpace(dpid,priority,flow_match,sliceActions):
        cmdString = 'fvctl --passwd-file=/root/.fvp addFlowSpace '+dpid+' '+priority+' '+flow_match+' '+sliceActions
        os.system(cmdString)
        print cmdString

#获取所有设备的dpid返回一个列表
def getDpidList():
        dpidList = []
        cmdString = "fvctl --passwd-file=/root/.fvp listDevices"
        dList = os.popen(cmdString).readlines()
        for dpid in dList:
                dpid = re.search('(?<=:\s).+',dpid).group()
                dpidList.append(dpid)
        return dpidList
#获取每一个dpid对应的端口号，返回一个字典
def getPort(dpid):
        portList={}
        cmdString = "fvctl --passwd-file=/root/.fvp getDeviceInfo " + dpid
        pList = os.popen(cmdString).readlines()
        pList[4] = re.search('(?<=portNames=).+',pList[4]).group()
        portlist = re.split(',',pList[4])
        for port in portlist:
                port_name=re.search('.+(?=\()',port).group()
                port_no=re.search('(?<=\()\d+',port).group()
                portList[port_name]=port_no
        return portList
#获取dpid和ovs的名称对应的字典
def getOVSName(dpidList):
    OVSNameDict={}
    for dpid in dpidList:
        cmdString = "fvctl --passwd-file=/root/.fvp getDeviceInfo " + dpid
        pList = os.popen(cmdString).readlines()
        pList[4] = re.search('[^,=]+?(?=\(65534)',pList[4]).group()
        OVSNameDict[pList[4]]=dpid
    return OVSNameDict

#create lxc dir
def createLxcDir(lxc):
    cmdString = "cp -R /var/lib/lxc/base /var/lib/lxc/"+lxc
    os.system(cmdString)
    print cmdString

#create lxc vm's config file
def createVmConfig(lxc,vmInterfaceList,usrName):
    f=open("/var/lib/lxc/"+lxc+"/config",'w')
    
    configString="lxc.utsname = "+lxc+"\n"
    for vmInterface in vmInterfaceList:
        configString+='''lxc.network.type = veth
lxc.network.flags = up
lxc.network.veth.pair = '''+usrName+"_"+vmInterface+"\n"
    configString+='''

lxc.tty = 4
lxc.pts = 1024
lxc.rootfs = /var/lib/lxc/'''+lxc+'''/rootfs
lxc.mount  = /var/lib/lxc/'''+lxc+'''/fstab

lxc.cgroup.devices.deny = a
# /dev/null and zero
lxc.cgroup.devices.allow = c 1:3 rwm
lxc.cgroup.devices.allow = c 1:5 rwm
# consoles
lxc.cgroup.devices.allow = c 5:1 rwm
lxc.cgroup.devices.allow = c 5:0 rwm
lxc.cgroup.devices.allow = c 4:0 rwm
lxc.cgroup.devices.allow = c 4:1 rwm
# /dev/{,u}random
lxc.cgroup.devices.allow = c 1:9 rwm
lxc.cgroup.devices.allow = c 1:8 rwm
lxc.cgroup.devices.allow = c 136:* rwm
lxc.cgroup.devices.allow = c 5:2 rwm
# rtc
lxc.cgroup.devices.allow = c 254:0 rwm'''
    f.write(configString)
    f.close()
    print lxc+" config file created"
#create lxc vm's fstab file
def createFstab(lxc):
    fstabString='''proc            /var/lib/lxc/'''+lxc+'''/rootfs/proc         proc    nodev,noexec,nosuid 0 0
devpts          /var/lib/lxc/'''+lxc+'''/rootfs/dev/pts      devpts defaults 0 0
sysfs           /var/lib/lxc/'''+lxc+'''/rootfs/sys          sysfs defaults  0 0'''
    f=open("/var/lib/lxc/"+lxc+"/fstab",'w')
    f.write(fstabString)
    f.close()
    print lxc+" fstab file created"

def createVmInterface(lxc,vmInterfaceList,vmInterfaceDict):
    interfaceString='''auto lo
iface lo inet loopback

'''
    i=0
    for vmInterface in vmInterfaceList:
        interfaceString+='''auto eth'''+str(i)+'''
iface eth'''+str(i)+''' inet static
    address '''+vmInterfaceDict[vmInterface]["ipv4address"]+'''
    netmask '''+vmInterfaceDict[vmInterface]["netmask"]+'''
    gateway '''+vmInterfaceDict[vmInterface]["gateway"]+"\n"
        i=i+1
    f=open("/var/lib/lxc/"+lxc+"/rootfs/etc/network/interfaces",'w')
    f.write(interfaceString)
    f.close()
    print lxc+" interface file created"
