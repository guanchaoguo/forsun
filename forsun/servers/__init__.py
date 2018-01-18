# -*- coding: utf-8 -*-
# 15/6/10
# create by: snower

import logging
import traceback
import threading
from tornado.ioloop import IOLoop
from thrift.protocol.TBinaryProtocol import TBinaryProtocolAcceleratedFactory
from torthrift.transport import TIOStreamTransportFactory
from torthrift.server import TTornadoServer
from processor.Forsun import Processor
from handler import Handler
from .. import config

class ThriftServer(object):
    def __init__(self, forsun):
        self.forsun = forsun
        self.server = None
        self.thread = None

    def serve(self):
        handler = Handler(self.forsun)
        processor = Processor(handler)
        tfactory = TIOStreamTransportFactory()
        protocol = TBinaryProtocolAcceleratedFactory()

        bind_address = config.get("SERVER_THRIFT_BIND_ADDRESS", "127.0.0.1")
        port = config.get("SERVER_THRIFT_PORT", 5643)
        self.server = TTornadoServer(processor, tfactory, protocol)
        self.server.bind(port, bind_address)
        self.server.start(1)
        ioloop = IOLoop.instance()
        logging.info("starting server by %s:%s", bind_address, port)
        ioloop.start()

    def start(self):
        def _():
            try:
                self.serve()
            except Exception as e:
                logging.error("thrift server error: %s\n%s", e, traceback.format_exc())

        self.thread = threading.Thread(target=_)
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        IOLoop.current().add_callback(lambda :IOLoop.current().stop())