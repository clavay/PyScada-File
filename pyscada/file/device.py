# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from time import time, sleep
from pyscada.device import GenericDevice
from .devices import GenericDevice as GenericHandlerDevice

import sys

import logging

logger = logging.getLogger(__name__)

try:
    import ftputil

    driver_ok = True
except ImportError:
    logger.error("Cannot import ftputil", exc_info=True)
    driver_ok = False


class Device(GenericDevice):
    """
    File device
    """

    def __init__(self, device):
        self.driver_ok = driver_ok
        self.handler_class = GenericHandlerDevice
        super().__init__(device)

        for var in self.device.variable_set.filter(active=1):
            if not hasattr(var, "visavariable"):
                continue
            self.variables[var.pk] = var

        if not self.driver_ok:
            logger.warning(f"Cannot import ftputil")
        if not self.driver_handler_ok:
            logger.warning(f"Cannot import handler for {self.device}")
