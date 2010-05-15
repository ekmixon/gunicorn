# -*- coding: utf-8 -
#
# This file is part of gunicorn released under the MIT license. 
# See the NOTICE for more information.

import logging
import optparse
import os

from gunicorn import __version__
from gunicorn import util
from gunicorn.arbiter import Arbiter
from gunicorn.config import Config
from gunicorn.debug import spew

class Application(object):
    """\
    An application interface for configuring and loading
    the various necessities for any given web framework.
    """
    def __init__(self, usage):
        self.log = logging.getLogger(__name__)
        self.cfg = Config(usage)
        
        parser = self.cfg.parser()
        opts, args = parser.parse_args()
        cfg = self.init(parser, opts, args)
        
        # Load up the any app specific configuration
        if cfg:
            for k, v in cfg:
                self.cfg.set(k.lower(), v)
        
        # Load up the config file if its found.
        if opts.config and os.path.exists(opts.config):
            cfg = globals().copy()
            try:
                execfile(opts.config, cfg, cfg)
            except Exception, e:
                print "Failed to read config file: %s" % opts.config
                traceback.print_exc()
                sys.exit(1)
        
            for k, v in cfg.iteritems():
                self.cfg.set(k.lower(), v)
            
        # Lastly, update the configuration with any command line
        # settings.
        for k, v in opts.__dict__.iteritems():
            if v is None or self.cfg.modified(k.lower()):
                continue
            self.cfg.set(k.lower(), v)
            
        self.configure_logging()
    
    def init(self, parser, opts, args):
        raise NotImplementedError
    
    def load(self):
        raise NotImplementedError
    
    def run(self):
        if self.cfg.spew:
            debug.spew()
        if self.cfg.daemon:
            util.daemonize()
        else:
            os.setpgrp()
        Arbiter(self).run()
    
    def configure_logging(self):
        """\
        Set the log level and choose the destination for log output.
        """
        logger = logging.getLogger('gunicorn')

        handlers = []
        if self.cfg.logfile != "-":
            handlers.append(logging.FileHandler(self.cfg.logfile))
        else:
            handlers.append(logging.StreamHandler())

        levels = {
            "critical": logging.CRITICAL,
            "error": logging.ERROR,
            "warning": logging.WARNING,
            "info": logging.INFO,
            "debug": logging.DEBUG
        }

        loglevel = levels.get(self.cfg.loglevel.lower(), logging.INFO)
        logger.setLevel(loglevel)
        
        format = r"%(asctime)s [%(process)d] [%(levelname)s] %(message)s"
        datefmt = r"%Y-%m-%d %H:%M:%S"
        for h in handlers:
            h.setFormatter(logging.Formatter(format, datefmt))
            logger.addHandler(h)

