#!/usr/bin/python
from re import compile

class byte:
    def __init__(self, value):
        if not isinstance(value, type(int())): raise Exception("NotInteger")
        self.value=value

    def __str__(self):
        tmp=list()
        address = self.value
        for i in range(4):
            tmp.insert(0, address & 255)
            address = address >> 8
        return "%d.%d.%d.%d" % tuple(tmp)

    def __tuple__(self):
        tmp=list()
        address = self.value
        for i in range(4):
            tmp.insert(0, address & 255)
            address = address >> 8
        return tmp


class IPv4:
    def __ip2int(self, ip):
        intaddress = 0
        for i in [int(i) for i in ip.split('.')]:
            intaddress = (intaddress << 8) + i
        return intaddress

    def __init__(self, ip, subnet = 32):
        validator = compile(".".join(["(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)" for i in range(4)]))
        if not validator.match(ip).group()==ip: raise Exception("NotIPAddress")
        subnet = int(subnet)
        if subnet > 32: raise Exception("NotNetworkMask")

        self.ip = byte(self.__ip2int(ip))
        self.intsubnet = subnet
        self.net = byte(int("1" * subnet,2)<<32-subnet)
        self.invnet = byte(int((bin(self.net.value)[2:].replace('1','3').replace('0', '1').replace('3','0')), 2))
        self.netaddr = byte(self.ip.value >> 32-subnet << 32-subnet)
        self.bcast = byte(self.netaddr.value + self.invnet.value)

        if subnet < 30:
            self.minhost = byte(self.netaddr.value + 1)
            self.maxhost = byte(self.netaddr.value + self.invnet.value - 1)
        else:
            self.minhost = byte(self.netaddr.value)
            self.maxhost = byte(self.netaddr.value + self.invnet.value)

    def __str__(self):
        return """Address: %s\nNetmask: %s\nWildcard: %s\n=>\nNetwork: %s/%s\nHostMin: %s\nHostMax: %s\nBroadcast: %s""" % (self.ip, self.net, self.invnet, self.netaddr, self.intsubnet, self.minhost, self.maxhost, self.bcast, )

    def innet(self, ip):
        try:
            intip = self.__ip2int(ip)
        except:
            return False

        if self.minhost.value <= intip and self.maxhost.value >= intip:
            return True
        else:
            return False

    def getfree(self, address_list, start=str()):
        ips = list()
        if len(start)>0:
            try:
                start = self.__ip2int(start)
            except:
                start = self.minhost.value
        else:
            start = self.minhost.value

        for ip in address_list:
            intip = self.__ip2int(ip)
            if intip >= self.minhost.value and intip <= self.maxhost.value and intip > start:
                ips.append(intip)
        ips.sort()

        try:
            return str(byte([i for i in range(start+1, self.maxhost.value) if not(i in ips)][0]))
        except:
            raise Exception("EndOfRange", "IP address range is is end")


if __name__=='__main__':
    from sys import argv
    addr, mask = "172.17.0.1", 24
    ip = IPv4(addr, mask)
    print ip
    print ip.innet(None)
    print ip.getfree(["172.17.0.1", "172.17.0.2", "172.17.0.3", "172.17.0.8", "172.17.0.5"])





