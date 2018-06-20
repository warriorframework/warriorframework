#!/usr/bin/python

##############################################################################
#                                                                            #
#  gNMI_Get.py                                                         #
#                                                                            #
#  History Change Log:                                                       #
#                                                                            #
#    1.0  [SW]  2017/06/02    first version                                  #
#    1.1  [SW]  2017/07/06    timeout behavior improved                      #
#    1.2  [SW]  2017/08/08    logging improved, options added                #
#                                                                            #
#  Objective:                                                                #
#                                                                            #
#    Testing tool for the gNMI (GRPC Network Management Interface) in Python #
#                                                                            #
#  Features supported:                                                       #
#                                                                            #
#    - gNMI Get (based on Nokia SROS 15.0 TLM feature-set)             #
#    - secure and insecure mode                                              #
#    - multiple subscriptions paths                                          #
#                                                                            #
#  Not yet supported:                                                        #
#                                                                            #
#    - Disable server name verification against TLS cert (opt: noHostCheck)  #
#    - Disable cert validation against root certificate (InsecureSkipVerify) #
#                                                                            #
#  License:                                                                  #
#                                                                            #
#    Licensed under the MIT license                                          #
#    See LICENSE.md delivered with this project for more information.        #
#                                                                            #
#  Author:                                                                   #
#                                                                            #
#    Sven Wisotzky                                                           #
#    mail:  sven.wisotzky(at)nokia.com                                       #
##############################################################################

"""
gNMI Get Client in Python Version 1.2
Copyright (C) 2017 Nokia. All Rights Reserved.
"""

__title__   = "gNMI_Get"
__version__ = "1.2"
__status__  = "released"
__author__  = "Sven Wisotzky"
__date__    = "2017 August 8th"

##############################################################################

import argparse
import re
import sys
import os
import logging
import time
from collections import OrderedDict

##############################################################################

def list_from_path(path='/'):
    if path:
        if path[0]=='/':
            if path[-1]=='/':
                #print('@@@@@ -1:', re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[1:-1])
                return re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[1:-1]
            else:
                #print('@@@@@ -1 else:', re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[1:])
                return re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[1:]
        else:
            if path[-1]=='/':
                #print('@@@@@ else -1:', re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[:-1])
                return re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[:-1]
            else:
                #print('@@@@@ else -1 else :', re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path))
                return re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)
    return []

def path_from_string(path='/'):
    mypath = []
    #print path

    for e in list_from_path(path):
        #print('@@@@@@@@@@@ e = ', e)
        eName = e.split("[", 1)[0]
        #print('eName = ', eName)
        eKeys = re.findall('\[(.*?)\]', e)
        #print('eKeys = ', eKeys)

        dKeys = {}
        #print eKeys

        for x in eKeys:
          dKeys = {}
          #print('@@@@@@@@@@@@@@ x = ', x)         #print x.split('=')[1]
          key = x.split('=')[0]
          value = x.split('=')[1]
          #dKeys = OrderedDict(key , value)
          dKeys[key] = value
          #print (gnmi_pb2.PathElem(name=eName, key=dKeys))

          mypath.append(gnmi_pb2.PathElem(name=eName, key = dKeys))

        if len(dKeys) == 0:

          #dKeys = OrderedDict(x.split('=', 1) for x in eKeys)
          #print('dKeys = ', dKeys)
          mypath.append(gnmi_pb2.PathElem(name=eName, key=dKeys))

    return gnmi_pb2.Path(elem=mypath)

'''
def gen_request( opt ):
    mysubs = []
    print(" options = %s" % opt.xpaths)
    for path in opt.xpaths:
        path_elements = list_from_path(path)
        #print('path_elements = %s' % path_elements)
        mypath = gnmi_pb2.Path(element=path_elements)
        print('mypath = %s' % mypath)

        #mysub = gnmi_pb2.Subscription(path=mypath, mode=opt.submode, suppress_redundant=opt.suppress, sample_interval=opt.interval*1000000000, heartbeat_interval=opt.heartbeat)
        #print('mysub = %s' % mysub)
        #mysubs.append(mysub)
        mysubs.append(mypath)

    if opt.prefix:
        pfx_elements = list_from_path(opt.prefix)
        myprefix = gnmi_pb2.Path(element=pfx_elements)
    else:
        myprefix = None

    if opt.qos:
        myqos = gnmi_pb2.QOSMarking(marking=opt.qos)
    else:
        myqos = None


    mygetreq = gnmi_pb2.GetRequest(prefix=myprefix, path = mysubs, type = opt.datatype, encoding=0)

    log.info('Sending GetRequest\n'+str(mygetreq))
    #yield mysubreq
    return mygetreq
'''

def gen_request( opt ):
    mysubs = []
    myoper = []

    operation = 0
    print('@@@@@@ operation = ', opt.operation)

    for path in opt.xpaths:
        mypath = path_from_string(path)
        #print(mypath)
        #mysub = gnmi_pb2.Subscription(path=mypath, mode=opt.submode, suppress_redundant=opt.suppress, sample_interval=opt.interval*1000000000, heartbeat_interval=opt.heartbeat)
        mysubs.append(mypath)

        #if opt.operation == 0:
        if opt.operation.lower() == "invalid":
          print('INVALID Set Operation')

        #elif opt.operation == 1:
        elif opt.operation.lower() == "delete":
          #print('DELETE Operation')
          operation = 1

        #elif opt.operation == 2:
        elif opt.operation.lower() == "replace":
          #print('REPLACE Operation')
          myoper.append(gnmi_pb2.Update(path = mypath))
          operation = 2

        else:
          #print('UPDATE Operation')
          myoper.append(gnmi_pb2.Update(path = mypath))
          operation = 3

    if opt.prefix:
        myprefix = path_from_string(opt.prefix)
    else:
        myprefix = None

    if opt.qos:
        myqos = gnmi_pb2.QOSMarking(marking=opt.qos)
    else:
        myqos = None

    if operation == 2:
      mysetreq = gnmi_pb2.SetRequest(prefix=myprefix, replace = myoper)
    elif operation == 3:
      mysetreq = gnmi_pb2.SetRequest(prefix=myprefix, update = myoper)
    elif operation == 1:
      mysetreq = gnmi_pb2.SetRequest(prefix=myprefix, delete = mysubs)

    #log.info('Sending SetRequest\n'+str(mysetreq))
    print('\n')
    return mysetreq

##############################################################################

if __name__ == '__main__':
    prog = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=prog+' '+__version__)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--quiet',   action='store_true', help='disable logging')
    group.add_argument('-v', '--verbose', action='count', help='enhanced logging')
    group = parser.add_argument_group()
    group.add_argument('--server', default='localhost:57400', help='server/port (default: localhost:57400)')
    group.add_argument('--username', default='admin', help='username (default: admin)')
    group.add_argument('--password', default='admin', help='password (default: admin)')
    group.add_argument('--cert', metavar='<filename>',  help='CA root certificate')
    group.add_argument('--tls', action='store_true', help='enable TLS security')
    group.add_argument('--ciphers', help='override environment "GRPC_SSL_CIPHER_SUITES"')
    group.add_argument('--altName', help='subjectAltName/CN override for server host validation')
    group.add_argument('--noHostCheck',  action='store_true', help='disable server host validation')

    group = parser.add_argument_group()
    group.add_argument('--logfile', metavar='<filename>', type=argparse.FileType('wb', 0), default='-', help='Specify the logfile (default: <stdout>)')
    group.add_argument('--stats', action='store_true', help='collect stats')

    group = parser.add_argument_group()
    #group.add_argument('--operation', default=3, type=int, help='operation [INVALID, DELETE, REPLACE, UPDATE]')
    group.add_argument('--operation', default='update', help='operation [INVALID, DELETE, REPLACE, UPDATE]')
    group.add_argument('--timeout', type=int, help='subscription duration in seconds (default: none)')
    group.add_argument('--heartbeat', type=int, help='heartbeat interval (default: none)')
    group.add_argument('--aggregate', action='store_true', help='allow aggregation')
    group.add_argument('--suppress', action='store_true', help='suppress redundant')
    group.add_argument('--submode', default=2, type=int, help='subscription mode [TARGET_DEFINED, ON_CHANGE, SAMPLE]')
    group.add_argument('--mode', default=0, type=int, help='[STREAM, ONCE, POLL]')
    group.add_argument('--datatype', default=0, type=int, help='[ALL, CONFIG, STATE, OPERATIONAL]')
    group.add_argument('--encoding', default=0, type=int, help='[JSON, BYTES, PROTO, ASCII, JSON_IETF]')
    group.add_argument('--qos', default=0, type=int, help='[JSON, BYTES, PROTO, ASCII, JSON_IETF]')
    group.add_argument('--use_alias',  action='store_true', help='use alias')
    group.add_argument('--prefix', default='', help='gRPC path prefix (default: none)')
    group.add_argument('xpaths', nargs=argparse.REMAINDER, help='path(s) to subscriber (default: /)')
    options = parser.parse_args()
    #username = input("username:")
    #password = input("password:")
    if len(options.xpaths)==0:
        options.xpaths=['/']

    if options.ciphers:
        os.environ["GRPC_SSL_CIPHER_SUITES"] = options.ciphers

    #  setup logging

    if options.quiet:
        loghandler = logging.NullHandler()
        loglevel = logging.NOTSET
    else:
        if options.verbose==None:
            logformat = '%(asctime)s,%(msecs)-3d %(message)s'
        else:
            logformat = '%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s %(message)s'

        if options.verbose==None or options.verbose==1:
            loglevel = logging.INFO
        else:
            loglevel = logging.DEBUG

        # For supported GRPC trace options check:
        #   https://github.com/grpc/grpc/blob/master/doc/environment_variables.md

        if options.verbose==3:
          os.environ["GRPC_TRACE"] = "all"
          os.environ["GRPC_VERBOSITY"] = "ERROR"

        if options.verbose==4:
          os.environ["GRPC_TRACE"] = "api,call_error,channel,connectivity_state,op_failure"
          os.environ["GRPC_VERBOSITY"] = "INFO"

        if options.verbose==5:
          os.environ["GRPC_TRACE"] = "all"
          os.environ["GRPC_VERBOSITY"] = "INFO"

        if options.verbose==6:
          os.environ["GRPC_TRACE"] = "all"
          os.environ["GRPC_VERBOSITY"] = "DEBUG"

        timeformat = '%y/%m/%d %H:%M:%S'
        loghandler = logging.StreamHandler(options.logfile)
        loghandler.setFormatter(logging.Formatter(logformat, timeformat))

    log = logging.getLogger(prog)
    log.setLevel(loglevel)
    log.addHandler(loghandler)

    try:
        import grpc
        import gnmi_pb2
    except ImportError as err:
        log.error(str(err))
        quit()

    if options.tls or options.cert:
        log.debug("Create SSL Channel")
        if options.cert:
            cred = grpc.ssl_channel_credentials(root_certificates=open(options.cert).read())
            opts = []
            if options.altName:
                opts.append(('grpc.ssl_target_name_override', options.altName,))
            if options.noHostCheck:
                log.error('Disable server name verification against TLS cert is not yet supported!')
                # TODO: Clarify how to setup gRPC with SSLContext using check_hostname:=False

            channel = grpc.secure_channel(options.server, cred, opts)
        else:
            log.error('Disable cert validation against root certificate (InsecureSkipVerify) is not yet supported!')
            # TODO: Clarify how to setup gRPC with SSLContext using verify_mode:=CERT_NONE

            cred = grpc.ssl_channel_credentials(root_certificates=None, private_key=None, certificate_chain=None)
            channel = grpc.secure_channel(options.server, cred)

    else:
        log.info("Create insecure Channel")
        channel = grpc.insecure_channel(options.server)

    log.debug("Create gNMI stub")
    stub = gnmi_pb2.gNMIStub(channel)

    req_iterator = gen_request( options )
    metadata = [('username',options.username), ('password', options.password)]

    msgs = 0
    upds = 0
    secs = 0
    start = 0

    try:
        responses = stub.Set(req_iterator, options.timeout, metadata=metadata)
        print(responses)

    except KeyboardInterrupt:
        log.info("%s stopped by user", prog)

    except grpc.RpcError as x:
        log.error("grpc.RpcError received:\n%s", x.details)

    except Exception as err:
        log.error(err)

    if (msgs>1):
        log.info("%d update messages received", msgs)

# EOF
