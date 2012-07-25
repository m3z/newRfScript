# -*- coding: utf-8 -*-
import os
import re

def startNox(component,port):
    cmdString = '''cd /usr/local/src/RouteFlow/rf-controller/build/src/;
./nox_core -v -i ptcp:'''+port+" "+component+" -d"
    os.system(cmdString)
    print cmdString
def startRf():
    cmdString="/usr/local/src/RouteFlow/build/rf-server &"
    os.system(cmdString)
    print cmdString


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


def ifconfig(interface, action, ip = None, netmask = None):
    if(ip and netmask):
        cmdString = 'ifconfig ' + interface + ' ' + action + \
                    ' ' + ip + ' netmask ' + netmask
    else:
        cmdString = 'ifconfig ' + interface + ' ' + action

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
    if(os.path.exists("/var/lib/lxc/"+lxc)):
        print "dir exist"
    else:
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


def createRfConfig(lxc,vmInterfaceList):
    f=open("/var/lib/lxc/"+lxc+"/config",'w')
    
    configString="lxc.utsname = "+lxc+'''
lxc.network.type = veth
lxc.network.flags = up
lxc.network.veth.pair = '''+lxc+".0\n"

    for vmInterface in vmInterfaceList:
        configString+='''lxc.network.type = veth
lxc.network.flags = up
lxc.network.veth.pair = '''+vmInterface+"\n"
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

def createRfInterface(lxc,vmInterfaceList,vmInterfaceDict,address):
    interfaceString='''auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address 192.168.1.'''+str(address)+'''
    netmask 255.255.255.0
'''
    i=1
    for vmInterface in vmInterfaceList:
        interfaceString+='''auto eth'''+str(i)+'''
iface eth'''+str(i)+''' inet static
    address '''+vmInterfaceDict[vmInterface]["ipv4address"]+'''
    netmask '''+vmInterfaceDict[vmInterface]["netmask"]+"\n"
        i=i+1
    f=open("/var/lib/lxc/"+lxc+"/rootfs/etc/network/interfaces",'w')
    f.write(interfaceString)
    f.close()
    print lxc+" interface file created"

def createDaemons(lxc,protocol):
    string = '''# This file tells the quagga package which daemons to start.
#
# Entries are in the format: <daemon>=(yes|no|priority)
#   0, "no"  = disabled
# This file tells the quagga package which daemons to start.
#
# Entries are in the format: <daemon>=(yes|no|priority)
#   0, "no"  = disabled
#   1, "yes" = highest priority
#   2 .. 10  = lower priorities
# Read /usr/share/doc/quagga/README.Debian for details.
#
# Sample configurations for these daemons can be found in
# /usr/share/doc/quagga/examples/.
#
# ATTENTION: 
#
# When activation a daemon at the first time, a config file, even if it is
# empty, has to be present *and* be owned by the user and group "quagga", else
# the daemon will not be started by /etc/init.d/quagga. The permissions should
# be u=rw,g=r,o=.
# When using "vtysh" such a config file is also needed. It should be owned by
# group "quaggavty" and set to ug=rw,o= though. Check /etc/pam.d/quagga, too.
#
zebra=yes
bgpd=no
ospfd=no
ospf6d=no
ripd=no
ripngd=no
isisd=no'''
    string=string.replace(protocol+"d=no",protocol+"d=yes")
    f=open("/var/lib/lxc/"+lxc+"/rootfs/etc/quagga/daemons","w")
    f.write(string)
    f.close()
    print lxc+" daemons created"

def createRipd(lxc,vmInterfaceList,vmInterfaceDict):
    string = '''! -*- rip -*-
!
! RIPd sample configuration file
!
! $Id: ripd.conf.sample,v 1.1 2002/12/13 20:15:30 paul Exp $
!
hostname ripd
password zebra
!
! debug rip events
! debug rip packet
!
router rip
'''
    for vmInterface in vmInterfaceList:
        string+=" network "+vmInterfaceDict[vmInterface]["segment"]+"\n"
    string +='''! network eth0
! route 10.0.0.0/8
! distribute-list private-only in eth0
!
!access-list private-only permit 10.0.0.0/8
!access-list private-only deny any
!
!log file /var/log/quagga/ripd.log
!
log stdout'''
    f=open("/var/lib/lxc/"+lxc+"/rootfs/etc/quagga/ripd.conf","w")
    f.write(string)
    f.close()
    print lxc+" ripd.conf created"

def createOspf(lxc,vmInterfaceList,vmInterfaceDict,address):
    string ='''!
! Example /etc/zebra/ospfd.conf configuration file
!
! Change the hostname to the name of your Access Point
hostname ospfd

! Set both of these passwords
password zebra
!enable password zebra

! Turn off welcome messages
!no banner motd

! Create an access list that allows access from localhost and nowhere else
!access-list access permit 127.0.0.1/32
!access-list access deny any

! Enable access control on the command-line interface
!line vty
!access-class access

'''
    for i in range(1,2):
        string+="interface eth"+str(i)+'''
 ip ospf dead-interval 20
 ip ospf hello-interval 5
'''
    
    string+='''! Enable routing
router ospf
 ospf router-id 192.168.1.'''+str(address)+"\n"
    for vmInterface in vmInterfaceList:
        string+=" network "+vmInterfaceDict[vmInterface]["segment"]+" area 0\n"
    for vmInterface in vmInterfaceList:
        string+=" no passive-interface "+vmInterfaceDict[vmInterface]["segment"]+"\n"
    string+='''! Enable authentication
!area 0 authentication

! Enable RFC-1583 compatibility to avoid routing loops
compatible rfc1583

! Enable logging
!log file /var/log/zebra/ospfd.log
log stdout'''
    f=open("/var/lib/lxc/"+lxc+"/rootfs/etc/quagga/ospfd.conf","w")
    f.write(string)
    f.close()
    print lxc+" ospfd.conf created"
    
