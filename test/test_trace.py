# -*- coding: utf-8 -*-


import pprint

import jspcap


trace = jspcap.tkextract(fin='../sample/http.pcap', nofile=True, verbose=True,
            trace=True, trace_format='pcap', trace_fout='../sample/trace')
pprint.pprint(trace.trace)