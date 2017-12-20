#!/usr/bin/python3
# -*- coding: utf-8 -*-


# Authentication Header
# Analyser for AH header


from .ipsec import IPsec


class AH(IPsec):

    ##########################################################################
    # Properties.
    ##########################################################################

    @property
    def name(self):
        return 'Authentication Header'

    @property
    def length(self):
        return self._info.len

    @property
    def protocol(self):
        return self._info.next

    ##########################################################################
    # Data models.
    ##########################################################################

    def __init__(self, _file, *, version):
        self._file = _file
        self._vers = version
        self._info = Info(self.read_ah())

    def __len__(self):
        return self._info.len

    def __length_hint__(self):
        return 20

    ##########################################################################
    # Utilities.
    ##########################################################################

    def read_ah(self):
        """Read Authentication Header.

        Structure of AH header [RFC 4302]:

             0                   1                   2                   3
             0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           | Next Header   |  Payload Len  |          RESERVED             |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |                 Security Parameters Index (SPI)               |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |                    Sequence Number Field                      |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |                                                               |
           +                Integrity Check Value-ICV (variable)           |
           |                                                               |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

            Octets          Bits          Name                Discription
              0              0          ah.next         Next Header
              1              8          ah.len          Payload Length
              2              16         ah.resv         Reserved (must be zero)
              4              32         ah.spi          Security Parameters Index (SPI)
              8              64         ah.seq          Sequence Number Field
              12             96         ah.icv          Integrity Check Value (ICV)

        """
        _next = self._read_protos(1)
        _plen = self._read_unpack(1)
        _resv = self._read_fileng(2)
        _scpi = self._read_unpack(4)
        _dsnf = self._read_unpack(4)

        # ICV length & value
        _tlen = 20 + _plen * 4
        _vlen = _tlen - 12
        _chkv = self._read_fileng(_vlen)

        ah = dict(
            next = _next,
            len = _tlen,
            resv = _resv,
            spi = _scpi,
            seq = dsnf,
            icv = _chkv,
        )

        if version == 4:
            _plen = 4 - (_vlen % 4)
        else:   # version == 6
            _plen = 8 - (_tlen % 8)
        if _plen:   # explicit padding in need
            ah['padding'] = self._read_fileng(_plen)

        return self._read_next_layer(ah, _next)