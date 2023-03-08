# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from .. import PROTOCOL_ID
from pyscada.models import DeviceProtocol
from pyscada.device import GenericHandlerDevice

import subprocess
import traceback
import os
from time import time
from pathlib import Path
import socket

import logging

logger = logging.getLogger(__name__)

driver_ok = True

try:
    import ftputil
except ImportError:
    logger.error("Cannot import ftputil")
    driver_ok = False

try:
    import paramiko
except ImportError:
    logger.error("Cannot import paramiko")
    driver_ok = False


class GenericDevice(GenericHandlerDevice):
    def __init__(self, pyscada_device, variables):
        super().__init__(pyscada_device, variables)
        self.driver_ok = driver_ok
        self._protocol = PROTOCOL_ID
        self.last_value = None
        self.my_session_factory = None
        self.t = None

    def connect(self):
        """
        establish a connection to the Instrument
        """
        super().connect()

        connected = True

        if self._device.filedevice.protocol == 0:
            # To handle the disconnect function
            class Inst:
                def close(self):
                    pass

            self.inst = Inst()

            file_path = self._device.filedevice.file_path
            try:
                open(file_path, "r")
            except FileNotFoundError:
                try:
                    Path(file_path).touch()
                    logger.info(f'{file_path} does not exit, touching it.')
                except PermissionError:
                    # logger.warning(f'pyscada user is not allowed to create the file {file_path}')
                    self._not_accessible_reason = f'pyscada user is not allowed to create the file {file_path}'
                    connected = False

        elif self._device.filedevice.protocol == 1:
            hostname = self._device.filedevice.host
            port = self._device.filedevice.port
            username = self._device.filedevice.username
            password = self._device.filedevice.password
            timeout = self._device.filedevice.timeout

            self.inst = paramiko.SSHClient()
            self.inst.load_system_host_keys()
            self.inst.set_missing_host_key_policy(paramiko.WarningPolicy())
            try:
                self.inst.connect(hostname, port, username, password, timeout=timeout)
            except (socket.gaierror, paramiko.ssh_exception.SSHException, OSError,
                    socket.timeout, paramiko.ssh_exception.AuthenticationException) as e:
                # logger.warning(e)
                self._not_accessible_reason = e
                self.inst = None
                connected = False

        elif self._device.filedevice.protocol == 2:
            self.my_session_factory = ftputil.session.session_factory(port=self._device.filedevice.port,
                                                                      use_passive_mode=self._device.filedevice.ftp_passive_mode,
                                                                      debug_level=0)

            try:
                self.inst = ftputil.FTPHost(self._device.filedevice.host,
                                            self._device.filedevice.username,
                                            self._device.filedevice.password,
                                            session_factory=self.my_session_factory)
            except ftputil.error.FTPOSError:
                pass
            except Exception as e:
                self._not_accessible_reason = e
                # logger.warning(traceback.format_exc())

            connected = self.download()

        self.accessibility()
        return connected

    def disconnect(self):
        if self.inst is not None:
            self.inst.close()
            self.inst = None
            return True
        return False

    def read_data(self, variable_instance):
        """
        read values from the device
        """
        value = None
        timeout = self._device.filedevice.timeout
        if "$value$" in variable_instance.filevariable.command:  # this is a writeable var
            return None
        if self._device.filedevice.protocol == 0:  # local file
            file_path = self._device.filedevice.file_path
            value = self.read_from_local_file(file_path, variable_instance, timeout)
        elif self._device.filedevice.protocol == 1:  # file over ssh
            if self.inst is None:
                logger.warning(f"Device {self._device} not connected. Cannot read file over ssh.")
                return None
            file_path = self._device.filedevice.file_path
            program = variable_instance.filevariable.program
            command = variable_instance.filevariable.command
            stdin, stdout, stderr = self.inst.exec_command(str(program) + ' ' + str(repr(command)) + ' ' + str(file_path),
                                                           timeout=timeout)
            value = stdout.read().decode()
            err = stderr.read().decode()
            if err != '':
                logger.warning(
                    f'{program} cmd ({command}) return an error : {err}')
                value = None
        elif self._device.filedevice.protocol == 2:  # file downloaded over ftp
            file_path = self._device.filedevice.local_temporary_file_copy_path
            value = self.read_from_local_file(file_path, variable_instance, timeout)

        return value

    def read_from_local_file(self, file_path, variable_instance, timeout):
        value = None
        try:
            open(file_path, "r")
            program = variable_instance.filevariable.program
            command = variable_instance.filevariable.command
            cmd = [program, command, file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            value = result.stdout

            if result.stderr != '':
                logger.warning(
                    f'{program} cmd ({command}) return an error : {result.stderr}')
            if result.returncode > 0:
                logger.warning(
                    f'{program} cmd ({command}) failed')
        except:
            logger.warning(traceback.format_exc())
        return value

    def write_data(self, variable_id, value, task):
        """
        write values to the device
        """
        try:
            if self.connect():
                for var in self._variables:
                    var = self._variables[var]
                    if variable_id == var.id:
                        timeout = self._device.filedevice.timeout

                        if var.dictionary is not None and len(var.dictionary.dictionaryitem_set.filter(value=int(value))):
                            value = var.dictionary.dictionaryitem_set.filter(value=int(value)).first().label

                        file_path = None
                        if self._device.filedevice.protocol == 0:  # local file
                            file_path = self._device.filedevice.file_path
                            self.write_to_local_file(self, file_path, var, timeout)

                        elif self._device.filedevice.protocol == 1:  # file over ssh
                            if self.inst is None:
                                logger.warning(f"Device {self._device} not connected. Cannot write file over ssh.")
                                return None
                            file_path = self._device.filedevice.file_path
                            program = var.filevariable.program
                            command = var.filevariable.command.replace('$value$', str(value))
                            stdin, stdout, stderr = self.inst.exec_command(
                                str(program) + ' ' + str(repr(command)) + ' ' + str(file_path),
                                timeout=timeout)
                            read_value = stdout.read().decode()
                            err = stderr.read().decode()
                            if err != '':
                                logger.warning(
                                    f'{program} cmd ({command}) return an error : {err}')
                                value = None
                            else:
                                self.inst.exec_command('echo ' + str(repr(read_value)) + ' > ' + str(file_path), timeout=timeout)

                        elif self._device.filedevice.protocol == 2:  # file downloaded over ftp
                            file_path = self._device.filedevice.local_temporary_file_copy_path
                            self.write_to_local_file(self, file_path, var, timeout)

                        self._device.filedevice.protocol < 2 or self.upload()
                        self.disconnect()
                        return value
                logger.warning(f'Variable {variable_id} not in variable list {self._variables} of device {self._device}')
            else:
                logger.warning(f'Write failed for {self._device}')
        except:
            logger.warning(traceback.format_exc())

        self.disconnect()
        return None

    def write_to_local_file(self, file_path, variable_instance, timeout):
        value = None
        try:
            cmd = [variable_instance.filevariable.program, str(variable_instance.filevariable.command).replace('$value$', str(value)),
                   file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            value = result.stdout

            if result.returncode == 0:
                if self._device.filedevice.protocol == 0 or self._device.filedevice.protocol == 2:
                    open(file_path, "w").write(str(value))
        except:
            logger.warning(traceback.format_exc())
        return value

    def download(self):
        try:
            if self._device.filedevice.protocol < 2:
                self._not_accessible_reason = "Wrong protocol"
                return False
            if self.inst is None:
                self._not_accessible_reason = f"Device {self._device} not connected. Cannot download file."
                return False
            if not hasattr(self.inst, 'path'):
                self._not_accessible_reason = "FTP instrument has not path functions"
                return False
            if self.inst.path.isfile(self._device.filedevice.file_path):
                self.inst.download(self._device.filedevice.file_path,
                                   self._device.filedevice.local_temporary_file_copy_path)
            else:
                self._not_accessible_reason = f'{self._device.filedevice.file_path} is not a file on FTP {self._device.filedevice.host}'
                return False
        except ftputil.error.FTPOSError as e:
            self._not_accessible_reason = f'FTP connection to {self._device} return {e}'
            return False
        except Exception as e:
            # logger.warning(traceback.format_exc())
            self._not_accessible_reason = e
            return False

        file_path = self._device.filedevice.local_temporary_file_copy_path
        try:
            open(file_path, "r")
        except FileNotFoundError:
            self._not_accessible_reason = f'Cannot open downloaded FTP file : {file_path}'
            return False
        return True

    def upload(self):
        try:
            if self._device.filedevice.protocol < 2:
                return False
            if self.inst is None:
                logger.warning(f"Device {self._device} not connected. Cannot upload file.")
                return False
            if os.path.isfile(self._device.filedevice.local_temporary_file_copy_path):
                self.inst.upload(self._device.filedevice.local_temporary_file_copy_path,
                                 self._device.filedevice.file_path)
                return True
            else:
                logger.warning(
                    f'{self._device.filedevice.local_temporary_file_copy_path} is not a file on localhost {self._device.filedevice.host}')
        except Exception as e:
            logger.warning(traceback.format_exc())
        return False
