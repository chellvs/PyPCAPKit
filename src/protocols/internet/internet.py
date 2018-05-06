# -*- coding: utf-8 -*-
"""root internet layer protocol

``jspcap.protocols.internet.internet`` contains both
``ETHERTYPE`` and ``Internet``. The former is a dictionary
of ethertype IEEE 802 numbers, registered in IANA. And the
latter is a base class for internet layer protocols, eg.
AH, IP, IPsec, IPv4, IPv6, IPX, and etc.

"""
# TODO: Implements ECN, ESP, ICMP, ICMPv6, IGMP, Shim6.


# Internet Layer Protocols
# Table of corresponding protocols


from jspcap.utilities import ProtoChain
from jspcap.protocols.protocol import Protocol
from jspcap.protocols.transport.transport import TP_PROTO


__all__ = ['Internet', 'ETHERTYPE']


# ##############################################################################
# # for unknown reason and never-encountered situation, at current time
# # we have to change the working directory to import from parent folders
#
# import os
# import sys
# sys.path.insert(1, os.path.join(sys.path[0], '..'))
#
# from protocol import Protocol
#
# del sys.path[1]
#
# # and afterwards, we recover the whole scene back to its original state
# ##############################################################################


# Ethertype IEEE 802 Numbers
ETHERTYPE = {
    # Link Layer
    0x0806 : 'ARP',     # Address Resolution Protocol
    0x8035 : 'RARP',    # Reverse Address Resolution Protocol
    0x8100 : 'VLAN',    # 802.1Q Customer VLAN Tag Type

    # Internet Layer
    0x0800 : 'IPv4',    # Internet Protocol version 4
    0x8137 : 'IPX',     # Internetwork Packet Exchange
    0x86dd : 'IPv6',    # Internet Protocol version 6
}


class Internet(Protocol):
    """Abstract base class for internet layer protocol family.

    Properties:
        * name -- str, name of corresponding procotol
        * info -- Info, info dict of current instance
        * alias -- str, acronym of corresponding procotol
        * layer -- str, `Internet`
        * length -- int, header length of corresponding protocol
        * protocol -- str, name of next layer protocol
        * protochain -- ProtoChain, protocol chain of current instance

    Attributes:
        * _file -- BytesIO, bytes to be extracted
        * _info -- Info, info dict of current instance
        * _protos -- ProtoChain, protocol chain of current instance

    Utilities:
        * _read_protos -- read next layer protocol type
        * _read_fileng -- read file buffer
        * _read_unpack -- read bytes and unpack to integers
        * _read_binary -- read bytes and convert into binaries
        * _decode_next_layer -- decode next layer protocol type
        * _import_next_layer -- import next layer protocol extractor

    """
    __layer__ = 'Internet'

    ##########################################################################
    # Properties.
    ##########################################################################

    # protocol layer
    @property
    def layer(self):
        """Protocol layer."""
        return self.__layer__

    ##########################################################################
    # Utilities.
    ##########################################################################

    def _read_protos(self, size):
        """Read next layer protocol type.

        Keyword arguments:
            size  -- int, buffer size

        """
        _byte = self._read_unpack(size)
        _prot = TP_PROTO.get(_byte)
        return _prot

    def _decode_next_layer(self, dict_, proto=None, length=None, *, version=4):
        """Decode next layer extractor.

        Keyword arguments:
            dict_ -- dict, info buffer
            proto -- str, next layer protocol name
            length -- int, valid (not padding) length
            version -- int, IP version
                        <4 / 6>

        """
        info, chain, alias = self._import_next_layer(proto, length, version=version)

        # make next layer protocol name
        if proto is None and chain:
            layer = chain.alias[0].lower()
            proto, chain = chain.tuple[0], None
        else:
            layer = str(alias or proto or 'Raw').lower()

        # write info and protocol chain into dict
        dict_[layer] = info
        self._protos = ProtoChain(proto, chain, alias)
        return dict_

    def _import_next_layer(self, proto, length=None, *, version=4, extension=False):
        """Import next layer extractor.

        Keyword arguments:
            proto -- str, next layer protocol name
            length -- int, valid (not padding) length
            version -- int, IP version (4/6)

        Protocols:
            * IPv4 -- internet layer
            * IPv6 -- internet layer
            * AH -- internet layer
            * TCP -- transport layer
            * UDP -- transport layer

        """
        if proto == 'AH':
            from jspcap.protocols.internet.ah import AH
            next_ = AH(self._file, length, version=version, extension=extension)
            return next_.info, next_.protochain, next_.alias
        elif proto == 'HIP':
            from jspcap.protocols.internet.hip import HIP
            next_ = HIP(self._file, length, extension=extension)
            return next_.info, next_.protochain, next_.alias
        elif proto == 'HOPOPT':
            from jspcap.protocols.internet.hopopt import HOPOPT
            next_ = HOPOPT(self._file, length, extension=extension)
            return next_.info, next_.protochain, next_.alias
        elif proto == 'IPv6-Frag':
            from jspcap.protocols.internet.ipv6_frag import IPv6_Frag
            next_ = IPv6_Frag(self._file, length, extension=extension)
            return next_.info, next_.protochain, next_.alias
        elif proto == 'IPv6-Opts':
            from jspcap.protocols.internet.ipv6_opts import IPv6_Opts
            next_ = IPv6_Opts(self._file, length, extension=extension)
            return next_.info, next_.protochain, next_.alias
        elif proto == 'IPv6-Route':
            from jspcap.protocols.internet.ipv6_route import IPv6_Route
            next_ = IPv6_Route(self._file, length, extension=extension)
            return next_.info, next_.protochain, next_.alias
        elif proto == 'MH':
            from jspcap.protocols.internet.mh import MH
            next_ = MH(self._file, length, extension=extension)
            return next_.info, next_.protochain, next_.alias
        elif proto == 'IPv4':
            from jspcap.protocols.internet.ipv4 import IPv4 as Protocol
        elif proto == 'IPv6':
            from jspcap.protocols.internet.ipv6 import IPv6 as Protocol
        elif proto == 'TCP':
            from jspcap.protocols.transport.tcp import TCP as Protocol
        elif proto == 'UDP':
            from jspcap.protocols.transport.udp import UDP as Protocol
        else:
            data = self._file.read(*[length]) or None
            return data, None, None
        next_ = Protocol(self._file, length)
        return next_.info, next_.protochain, next_.alias