# ----------------------------------------------------------------------------
# Copyright (C) 2017 Verizon.  All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ----------------------------------------------------------------------------

'''IANA Protocol numbers.
See http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml.

The ``protocol_numbers`` module provides IANA protocol name and number
descriptions and translation back and forth between name and number.

The module constant ``BY_NAME`` defines a mapping
from protocol name to a record with the corresponding IANA protocol
number and description.

    ::

        >>> protocol_numbers.BY_NUMBER['TCP']
        {'number': '6', 'description': 'Transmission Control'}


Conversely, the module constant ``BY_NUMBER`` defines a mapping
from protocol number to a record with the corresponding IANA protocol
name and description.

    ::

        >>> protocol_numbers.BY_NAME[6]
        {'protocol': 'TCP', 'description': 'Transmission Control'}



'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def record_by_number(proto_num):
    '''Return the protocol record for a protocol number.

    If no protocol exists with protocol number ``proto_num``, ``None``
    is returned.

    Example::

        >>> protocol_numbers.record_by_number(6)
        {'number': 'TCP', 'description': 'Transmission Control'}

    '''
    if proto_num in BY_NUMBER:
        return BY_NUMBER[proto_num]
    return None


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def record_by_name(proto_name):
    '''Return the protocol record for a protocol name.

    If no protocol named ``proto_name`` exists, ``None``
    is returned.

    Example::

        >>> protocol_numbers.record_by_name('TCP')
        {'number': '6', 'description': 'Transmission Control'}

    '''
    if proto_name in BY_PROTOCOL:
        return BY_PROTOCOL[proto_name]
    return None


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def name_of_protocol_number(proto_num):
    '''Return the name of a protocol given by number.

    If no protocol exists with protocol number ``proto_num``, ``None``
    is returned.

    Example::

        >>> protocol_numbers.name_of_protocol_number(6)
        'TCP'

    '''
    record = record_by_number(proto_num)
    return record['protocol'] if record else None


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def number_of_protocol_name(proto_name):
    '''Return the number of a protocol given by name.

    If no protocol named ``proto_name`` exists, ``None``
    is returned.

    Example::

        >>> protocol_numbers.number_of_protocol_name('TCP')
        6

    '''
    record = record_by_name(proto_name)
    return record['number'] if record else None

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
BY_NUMBER = {
    0: {
        'protocol': 'HOPOPT',
        'description': 'IPv6 Hop-by-Hop Option'
        },

    1: {
        'protocol': 'ICMP',
        'description': 'Internet Control Message'
        },

    2: {
        'protocol': 'IGMP',
        'description': 'Internet Group Management'
        },

    3: {
        'protocol': 'GGP',
        'description': 'Gateway-to-Gateway'
        },

    4: {
        'protocol': 'IPv4',
        'description': 'IPv4 encapsulation'
        },

    5: {
        'protocol': 'ST',
        'description': 'Stream'
        },

    6: {
        'protocol': 'TCP',
        'description': 'Transmission Control'
        },

    7: {
        'protocol': 'CBT',
        'description': 'CBT'
        },

    8: {
        'protocol': 'EGP',
        'description': 'Exterior Gateway Protocol'
        },

    9: {
        'protocol': 'IGP',
        'description': (
            'any private interior gateway (used by Cisco for their IGRP)'
            )
        },

    10: {
        'protocol': 'BBN-RCC-MON',
        'description': 'BBN RCC Monitoring'
        },

    11: {
        'protocol': 'NVP-II',
        'description': 'Network Voice Protocol'
        },

    12: {
        'protocol': 'PUP',
        'description': 'PUP'
        },

    13: {
        'protocol': 'ARGUS (deprecated)',
        'description': 'ARGUS'
        },

    14: {
        'protocol': 'EMCON',
        'description': 'EMCON'
        },

    15: {
        'protocol': 'XNET',
        'description': 'Cross Net Debugger'
        },

    16: {
        'protocol': 'CHAOS',
        'description': 'Chaos'
        },

    17: {
        'protocol': 'UDP',
        'description': 'User Datagram'
        },

    18: {
        'protocol': 'MUX',
        'description': 'Multiplexing'
        },

    19: {
        'protocol': 'DCN-MEAS',
        'description': 'DCN Measurement Subsystems'
        },

    20: {
        'protocol': 'HMP',
        'description': 'Host Monitoring'
        },

    21: {
        'protocol': 'PRM',
        'description': 'Packet Radio Measurement'
        },

    22: {
        'protocol': 'XNS-IDP',
        'description': 'XEROX NS IDP'
        },

    23: {
        'protocol': 'TRUNK-1',
        'description': 'Trunk-1'
        },

    24: {
        'protocol': 'TRUNK-2',
        'description': 'Trunk-2'
        },

    25: {
        'protocol': 'LEAF-1',
        'description': 'Leaf-1'
        },

    26: {
        'protocol': 'LEAF-2',
        'description': 'Leaf-2'
        },

    27: {
        'protocol': 'RDP',
        'description': 'Reliable Data Protocol'
        },

    28: {
        'protocol': 'IRTP',
        'description': 'Internet Reliable Transaction'
        },

    29: {
        'protocol': 'ISO-TP4',
        'description': 'ISO Transport Protocol Class 4'
        },

    30: {
        'protocol': 'NETBLT',
        'description': 'Bulk Data Transfer Protocol'
        },

    31: {
        'protocol': 'MFE-NSP',
        'description': 'MFE Network Services Protocol'
        },

    32: {
        'protocol': 'MERIT-INP',
        'description': 'MERIT Internodal Protocol'
        },

    33: {
        'protocol': 'DCCP',
        'description': 'Datagram Congestion Control Protocol'
        },

    34: {
        'protocol': '3PC',
        'description': 'Third Party Connect Protocol'
        },

    35: {
        'protocol': 'IDPR',
        'description': 'Inter-Domain Policy Routing Protocol'
        },

    36: {
        'protocol': 'XTP',
        'description': 'XTP'
        },

    37: {
        'protocol': 'DDP',
        'description': 'Datagram Delivery Protocol'
        },

    38: {
        'protocol': 'IDPR-CMTP',
        'description': 'IDPR Control Message Transport Proto'
        },

    39: {
        'protocol': 'TP++',
        'description': 'TP++ Transport Protocol'
        },

    40: {
        'protocol': 'IL',
        'description': 'IL Transport Protocol'
        },

    41: {
        'protocol': 'IPv6',
        'description': 'IPv6 encapsulation'
        },

    42: {
        'protocol': 'SDRP',
        'description': 'Source Demand Routing Protocol'
        },

    43: {
        'protocol': 'IPv6-Route',
        'description': 'Routing Header for IPv6'
        },

    44: {
        'protocol': 'IPv6-Frag',
        'description': 'Fragment Header for IPv6'
        },

    45: {
        'protocol': 'IDRP',
        'description': 'Inter-Domain Routing Protocol'
        },

    46: {
        'protocol': 'RSVP',
        'description': 'Reservation Protocol'
        },

    47: {
        'protocol': 'GRE',
        'description': 'Generic Routing Encapsulation'
        },

    48: {
        'protocol': 'DSR',
        'description': 'Dynamic Source Routing Protocol'
        },

    49: {
        'protocol': 'BNA',
        'description': 'BNA'
        },

    50: {
        'protocol': 'ESP',
        'description': 'Encap Security Payload'
        },

    51: {
        'protocol': 'AH',
        'description': 'Authentication Header'
        },

    52: {
        'protocol': 'I-NLSP',
        'description': 'Integrated Net Layer Security  TUBA'
        },

    53: {
        'protocol': 'SWIPE (deprecated)',
        'description': 'IP with Encryption'
        },

    54: {
        'protocol': 'NARP',
        'description': 'NBMA Address Resolution Protocol'
        },

    55: {
        'protocol': 'MOBILE',
        'description': 'IP Mobility'
        },

    56: {
        'protocol': 'TLSP',
        'description': (
            'Transport Layer Security Protocol using Kryptonet key management'
            )
        },

    57: {
        'protocol': 'SKIP',
        'description': 'SKIP'
        },

    58: {
        'protocol': 'IPv6-ICMP',
        'description': 'ICMP for IPv6'
        },

    59: {
        'protocol': 'IPv6-NoNxt',
        'description': 'No Next Header for IPv6'
        },

    60: {
        'protocol': 'IPv6-Opts',
        'description': 'Destination Options for IPv6'
        },

    61: {
        'protocol': '',
        'description': 'any host internal protocol'
        },

    62: {
        'protocol': 'CFTP',
        'description': 'CFTP'
        },

    63: {
        'protocol': '',
        'description': 'any local network'
        },

    64: {
        'protocol': 'SAT-EXPAK',
        'description': 'SATNET and Backroom EXPAK'
        },

    65: {
        'protocol': 'KRYPTOLAN',
        'description': 'Kryptolan'
        },

    66: {
        'protocol': 'RVD',
        'description': 'MIT Remote Virtual Disk Protocol'
        },

    67: {
        'protocol': 'IPPC',
        'description': 'Internet Pluribus Packet Core'
        },

    68: {
        'protocol': '',
        'description': 'any distributed file system'
        },

    69: {
        'protocol': 'SAT-MON',
        'description': 'SATNET Monitoring'
        },

    70: {
        'protocol': 'VISA',
        'description': 'VISA Protocol'
        },

    71: {
        'protocol': 'IPCV',
        'description': 'Internet Packet Core Utility'
        },

    72: {
        'protocol': 'CPNX',
        'description': 'Computer Protocol Network Executive'
        },

    73: {
        'protocol': 'CPHB',
        'description': 'Computer Protocol Heart Beat'
        },

    74: {
        'protocol': 'WSN',
        'description': 'Wang Span Network'
        },

    75: {
        'protocol': 'PVP',
        'description': 'Packet Video Protocol'
        },

    76: {
        'protocol': 'BR-SAT-MON',
        'description': 'Backroom SATNET Monitoring'
        },

    77: {
        'protocol': 'SUN-ND',
        'description': 'SUN ND PROTOCOL-Temporary'
        },

    78: {
        'protocol': 'WB-MON',
        'description': 'WIDEBAND Monitoring'
        },

    79: {
        'protocol': 'WB-EXPAK',
        'description': 'WIDEBAND EXPAK'
        },

    80: {
        'protocol': 'ISO-IP',
        'description': 'ISO Internet Protocol'
        },

    81: {
        'protocol': 'VMTP',
        'description': 'VMTP'
        },

    82: {
        'protocol': 'SECURE-VMTP',
        'description': 'SECURE-VMTP'
        },

    83: {
        'protocol': 'VINES',
        'description': 'VINES'
        },

    # Protocol TTP is deprecated; in practice, 84 == IPTM.
    # 84: {
    #     'protocol': 'TTP',
    #     'description': 'Transaction Transport Protocol'
    #     },

    84: {
        'protocol': 'IPTM',
        'description': 'Internet Protocol Traffic Manager'
        },

    85: {
        'protocol': 'NSFNET-IGP',
        'description': 'NSFNET-IGP'
        },

    86: {
        'protocol': 'DGP',
        'description': 'Dissimilar Gateway Protocol'
        },

    87: {
        'protocol': 'TCF',
        'description': 'TCF'
        },

    88: {
        'protocol': 'EIGRP',
        'description': 'EIGRP'
        },

    89: {
        'protocol': 'OSPFIGP',
        'description': 'OSPFIGP'
        },

    90: {
        'protocol': 'Sprite-RPC',
        'description': 'Sprite RPC Protocol'
        },

    91: {
        'protocol': 'LARP',
        'description': 'Locus Address Resolution Protocol'
        },

    92: {
        'protocol': 'MTP',
        'description': 'Multicast Transport Protocol'
        },

    93: {
        'protocol': 'AX.25',
        'description': 'AX.25 Frames'
        },

    94: {
        'protocol': 'IPIP',
        'description': 'IP-within-IP Encapsulation Protocol'
        },

    95: {
        'protocol': 'MICP (deprecated)',
        'description': 'Mobile Internetworking Control Pro.'
        },

    96: {
        'protocol': 'SCC-SP',
        'description': 'Semaphore Communications Sec. Pro.'
        },

    97: {
        'protocol': 'ETHERIP',
        'description': 'Ethernet-within-IP Encapsulation'
        },

    98: {
        'protocol': 'ENCAP',
        'description': 'Encapsulation Header'
        },

    99: {
        'protocol': '',
        'description': 'any private encryption scheme'
        },

    100: {
        'protocol': 'GMTP',
        'description': 'GMTP'
        },

    101: {
        'protocol': 'IFMP',
        'description': 'Ipsilon Flow Management Protocol'
        },

    102: {
        'protocol': 'PNNI',
        'description': 'PNNI over IP'
        },

    103: {
        'protocol': 'PIM',
        'description': 'Protocol Independent Multicast'
        },

    104: {
        'protocol': 'ARIS',
        'description': 'ARIS'
        },

    105: {
        'protocol': 'SCPS',
        'description': 'SCPS'
        },

    106: {
        'protocol': 'QNX',
        'description': 'QNX'
        },

    107: {
        'protocol': 'A/N',
        'description': 'Active Networks'
        },

    108: {
        'protocol': 'IPComp',
        'description': 'IP Payload Compression Protocol'
        },

    109: {
        'protocol': 'SNP',
        'description': 'Sitara Networks Protocol'
        },

    110: {
        'protocol': 'Compaq-Peer',
        'description': 'Compaq Peer Protocol'
        },

    111: {
        'protocol': 'IPX-in-IP',
        'description': 'IPX in IP'
        },

    112: {
        'protocol': 'VRRP',
        'description': 'Virtual Router Redundancy Protocol'
        },

    113: {
        'protocol': 'PGM',
        'description': 'PGM Reliable Transport Protocol'
        },

    114: {
        'protocol': '',
        'description': 'any 0-hop protocol'
        },

    115: {
        'protocol': 'L2TP',
        'description': 'Layer Two Tunneling Protocol'
        },

    116: {
        'protocol': 'DDX',
        'description': 'D-II Data Exchange (DDX)'
        },

    117: {
        'protocol': 'IATP',
        'description': 'Interactive Agent Transfer Protocol'
        },

    118: {
        'protocol': 'STP',
        'description': 'Schedule Transfer Protocol'
        },

    119: {
        'protocol': 'SRP',
        'description': 'SpectraLink Radio Protocol'
        },

    120: {
        'protocol': 'UTI',
        'description': 'UTI'
        },

    121: {
        'protocol': 'SMP',
        'description': 'Simple Message Protocol'
        },

    122: {
        'protocol': 'SM (deprecated)',
        'description': 'Simple Multicast Protocol'
        },

    123: {
        'protocol': 'PTP',
        'description': 'Performance Transparency Protocol'
        },

    124: {
        'protocol': 'ISIS over IPv4',
        'description': ''
        },

    125: {
        'protocol': 'FIRE',
        'description': ''
        },

    126: {
        'protocol': 'CRTP',
        'description': 'Combat Radio Transport Protocol'
        },

    127: {
        'protocol': 'CRUDP',
        'description': 'Combat Radio User Datagram'
        },

    128: {
        'protocol': 'SSCOPMCE',
        'description': ''
        },

    129: {
        'protocol': 'IPLT',
        'description': ''
        },

    130: {
        'protocol': 'SPS',
        'description': 'Secure Packet Shield'
        },

    131: {
        'protocol': 'PIPE',
        'description': 'Private IP Encapsulation within IP'
        },

    132: {
        'protocol': 'SCTP',
        'description': 'Stream Control Transmission Protocol'
        },

    133: {
        'protocol': 'FC',
        'description': 'Fibre Channel'
        },

    134: {
        'protocol': 'RSVP-E2E-IGNORE',
        'description': ''
        },

    135: {
        'protocol': 'Mobility Header',
        'description': ''
        },

    136: {
        'protocol': 'UDPLite',
        'description': ''
        },

    137: {
        'protocol': 'MPLS-in-IP',
        'description': ''
        },

    138: {
        'protocol': 'manet',
        'description': 'MANET Protocols'
        },

    139: {
        'protocol': 'HIP',
        'description': 'Host Identity Protocol'
        },

    140: {
        'protocol': 'Shim6',
        'description': 'Shim6 Protocol'
        },

    141: {
        'protocol': 'WESP',
        'description': 'Wrapped Encapsulating Security Payload'
        },

    142: {
        'protocol': 'ROHC',
        'description': 'Robust Header Compression'
        },

    # 143-252: {
    #     'protocol': '',
    #     'description': 'Unassigned'
    #     },

    253: {
        'protocol': '',
        'description': 'Use for experimentation and testing'
        },

    254: {
        'protocol': '',
        'description': 'Use for experimentation and testing'
        },

    255: {
        'protocol': 'Reserved',
        'description': ''
        },
    }


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
BY_PROTOCOL = {}
for (num, proto) in BY_NUMBER.iteritems():
    BY_PROTOCOL[proto['protocol']] = {
        'number': num,
        'description': proto['description']
        }
