#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from pkgutil import extend_path

# from mptcpanalyzer.core import get_basename
import logging
import numpy as np
# import os
# from . import plot
# from .core import load_fields_to_export_from_file

# __path__ = extend_path(__path__, __name__)


# h = logging.FileHandler(".mptcpanalyzer-" + str(os.getpid()), delay=True)
# TODO let final script set the handler
handler = logging.FileHandler("mptcpanalyzer.log", delay=False)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.CRITICAL)


# table_name = "connections"

# __exporter__ = None
# __all__ = [
    # "table_name",
# ]


from collections import namedtuple

MpTcpSubflow = namedtuple('Subflow', ['ipsrc', 'ipdst', 'sport', 'dport'])
Field = namedtuple('Field', ['fullname', 'name', 'type', 'plottable' ])


def get_fields (field , field2=None):

    # def name(s):
        # return s[0] if isinstance(s, tuple) else s
        # return map(name, d.values())
    # fields_v2()
    l = fields_v2()
    keys = map ( lambda x: getattr(x, field), l)
    if field2 is None:
        return keys

    return dict(zip (keys, map ( lambda x: getattr(x, field2), l)))
    # return dict( 
    #             zip( d.keys(), map(name, d.values()) ) 
    #             )
    # return dict((v,a) for k,a,*v in a.iteritems())

    # print("== tata", dict(get_default_fields()))
# toto = _get_wireshark_mptcpanalyzer_mappings( get_default_fields() )

# data.rename (inplace=True, columns=toto)

def fields_v2():
    l = [
            Field("frame.number", "packetid", None, False),
            Field("frame.time_relative", "reltime", None, False),
            Field("frame.time_delta", "time_delta", None, False),
            Field("frame.time_epoch", "abstime", None, False),
            # Field("frame.time_delta", "time_delta", None, False),
            Field("_ws.col.ipsrc", "ipsrc", None, False),
            Field("_ws.col.ipdst", "ipdst", str, False),

            Field("mptcp.dsn", "dsn", np.float64, True),
            # "mptcp.rawdsn64":        "dsnraw64",
            # "mptcp.ack":        "dack",
            Field("tcp.stream", "tcpstream", np.float64, True),
            Field("mptcp.stream", "mptcpstream", None, False),
            Field("tcp.srcport", "sport", None, False),
            Field("tcp.dstport", "dport", None, False),
            # rawvalue is tcp.window_size_value
            # tcp.window_size takes into account scaling factor !
            Field("tcp.window_size", "rwnd", None, True),
            Field("tcp.options.mptcp.sendkey", "sendkey", None, False),
            Field("tcp.options.mptcp.recvkey", "recvkey", None, True),
            Field("tcp.options.mptcp.recvtok", "recvtok", None, False),
            Field("tcp.options.mptcp.datafin.flag", "datafin", None, False),
            Field("tcp.options.mptcp.subtype", "subtype", None, False),
            Field("tcp.flags", "tcpflags", None, False),
            Field("tcp.options.mptcp.rawdataseqno", "dss_dsn", None, True),
            Field("tcp.options.mptcp.rawdataack", "dss_rawack",None, True),
            Field("tcp.options.mptcp.subflowseqno", "dss_ssn", None, True),
            Field("tcp.options.mptcp.datalvllen", "dss_length",None, True),
            Field("tcp.options.mptcp.addrid", "addrid", None, False),
            Field("mptcp.master", "master", None, True),
            Field("tcp.seq", "tcpseq", np.float64, True),
            Field("tcp.len", "tcplen", np.float64, True),
            Field("mptcp.dsn", "dsn", None, True),
            Field("mptcp.rawdsn64", "dsnraw64", np.float64, True),
            Field("mptcp.ack", "dack", None, True),
        ]
    return l

def get_default_fields():
    """
    TODO should accept filters :)

    Mapping between short names easy to use as a column title (in a CSV file) 
    and the wireshark field name
    There are some specific fields that require to use -o instead, 
    see tshark -G column-formats

    CAREFUL: when setting the type to int, pandas will throw an error if there
    are still NAs in the column. Relying on float64 permits to overcome this.

ark.exe -r file.pcap -T fields -E header=y -e frame.number -e col.AbsTime -e col.DeltaTime -e col.Source -e col.Destination -e col.Protocol -e col.Length -e col.Info
"""

    return {
            "frame.number":        ("packetid",),
            # reestablish once format is changed (see options)
            # "time": "frame.time",
            "frame.time_relative":        "reltime",
            "frame.time_delta":        "time_delta",
            # "frame.time":        "abstime",
            "frame.time_epoch":        "abstime",
            # "ipsrc": "_ws.col.Source",
            # "ipdst": "_ws.col.Destination",
            "_ws.col.ipsrc" : "ipsrc",
            "_ws.col.ipdst" : "ipdst",
            # "_ws.col.AbsTime": "abstime2",
            # "_ws.col.DeltaTime": "deltatime",
            # "ip.src":        "ipsrc",
            # "ip.dst":        "ipdst",
            "tcp.stream":        ("tcpstream", np.int64),
            "mptcp.stream":        "mptcpstream",
            "tcp.srcport":        "sport",
            "tcp.dstport":        "dport",
            # rawvalue is tcp.window_size_value
            # tcp.window_size takes into account scaling factor !
            "tcp.window_size":        "rwnd",
            "tcp.options.mptcp.sendkey"        : "sendkey",
            "tcp.options.mptcp.recvkey"        : "recvkey",
            "tcp.options.mptcp.recvtok"        : "recvtok",
            "tcp.options.mptcp.datafin.flag":        "datafin",
            "tcp.options.mptcp.subtype":        ("subtype", np.float64),
            "tcp.flags":        "tcpflags",
            "tcp.options.mptcp.rawdataseqno":        "dss_dsn",
            "tcp.options.mptcp.rawdataack":        "dss_rawack",
            "tcp.options.mptcp.subflowseqno":        "dss_ssn",
            "tcp.options.mptcp.datalvllen":        "dss_length",
            "tcp.options.mptcp.addrid":        "addrid",
            "mptcp.master":        "master",
            # TODO add sthg related to mapping analysis ?
            "tcp.seq":        ("tcpseq", np.float64),
            "tcp.len":        ("tcplen", np.float64),
            "mptcp.dsn":        "dsn",
            "mptcp.rawdsn64":        "dsnraw64",
            "mptcp.ack":        "dack",
        }

__default_fields__ = get_default_fields()
