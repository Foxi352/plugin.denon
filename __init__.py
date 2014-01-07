#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2014 Serge Wagener                               serge@swa.lu
#########################################################################
#  Denon-Plugin for SmartHome.py.    http://mknx.github.io/smarthome/
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging

import lib.connection

logger = logging.getLogger('Denon')


class Denon(lib.connection.Client):

    # Initialize connection to receiver
    def __init__(self, smarthome, host, port=23):
        logger.info("Denon: connecting to {0}:{1}".format(host, port))
        lib.connection.Client.__init__(self, host, port, monitor=True)
        self.terminator = b'\r'
        self._sh = smarthome
        self._power = ''

    # Parse received input from Denon and set items
    def found_terminator(self, data):
        data = data.decode()
        logger.debug("Denon: Got: {0}".format(data))
        if data == 'PWON':
            logger.debug("Denon: Powered on")
            self._power(True, 'Denon')
        elif data == 'PWSTANDBY':
            logger.debug("Denon: Powered off")
            self._power(False, 'Denon')

    # Set plugin to alive
    def run(self):
        self.alive = True

    # Close connection to receiver and set alive to false
    def stop(self):
        self.alive = False
        self.close()

    # Parse items and bind commands to plugin
    def parse_item(self, item):
        if 'denon_send' in item.conf:
            cmd = item.conf['denon_send']
            if (cmd is None):
                return None
            if cmd == 'power':
                self._power = item
            return self.update_item
        else:
            return None

    # TODO: Logic not yet used
    def parse_logic(self, logic):
        pass

    # Receive commands, process them and forward them to receiver
    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Denon':
            if 'denon_send' in item.conf:
                command = item.conf['denon_send']
                value = item()
                logger.info("Denon: {0} set {1} to {2} for {3}".format(caller, command, value, item.id()))
                if(command == 'power') and (isinstance(value, bool)):
                    self._send('PWON' if value else 'PWSTANDBY')
                else:
                    logger.warning("Denon: Command {0} or value {1} invalid".format(command, value))

    # Send commands to receiver if connected
    def _send(self, cmd):
        if not self.connected:
            logger.warning("Denon: No connection, can not send command: {0}".format(cmd))
            return
        logger.debug("Denon: Sending request: {0}".format(cmd))
        self.send(bytes(cmd + '\r', 'utf-8'))

# TODO: Delete everything below :-)

'''
2014-01-07 17:09:07,511 INFO     Main         Denon: Visu send EG.Stube.Denon.Power  - power True -- 2014-01-07 17:09:07,515 DEBUG    Main         Denon: Sending request: PWON -- __init__.py:_send:101

2014-01-07 17:09:07,536 DEBUG    Main         Denon: Got: ZMON -- __init__.py:found_terminator:40
2014-01-07 17:09:08,066 DEBUG    Main         Denon: Got: PWON -- __init__.py:found_terminator:40
2014-01-07 17:09:29,803 DEBUG    Main         Denon: Sending request: PWSTANDBY -- __init__.py:_send:101
2014-01-07 17:09:29,827 DEBUG    Main         Denon: Got: PWSTANDBY -- __init__.py:found_terminator:40
2014-01-07 17:09:30,322 DEBUG    Main         Denon: Got: ZMOFF -- __init__.py:found_terminator:40
2014-01-07 17:26:49,874 DEBUG    Main         Denon: Got: MSDIRECT -- __init__.py:found_terminator:40
2014-01-07 17:26:49,899 DEBUG    Main         Denon: Got: PSDCO OFF -- __init__.py:found_terminator:40
2014-01-07 17:26:49,940 DEBUG    Main         Denon: Got: PSDRC AUTO -- __init__.py:found_terminator:40
2014-01-07 17:26:49,993 DEBUG    Main         Denon: Got: PSLFE 00 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,020 DEBUG    Main         Denon: Got: PSBAS 50 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,060 DEBUG    Main         Denon: Got: PSTRE 50 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,101 DEBUG    Main         Denon: Got: PSTONE CTRL OFF -- __init__.py:found_terminator:40
2014-01-07 17:26:50,150 DEBUG    Main         Denon: Got: SIDVD -- __init__.py:found_terminator:40
2014-01-07 17:26:50,181 DEBUG    Main         Denon: Got: CVFL 44 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,219 DEBUG    Main         Denon: Got: CVFR 475 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,259 DEBUG    Main         Denon: Got: CVC 46 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,312 DEBUG    Main         Denon: Got: CVSW 38 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,340 DEBUG    Main         Denon: Got: CVSL 485 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,380 DEBUG    Main         Denon: Got: CVSR 49 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,421 DEBUG    Main         Denon: Got: CVSBL 50 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,459 DEBUG    Main         Denon: Got: CVSBR 50 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,498 DEBUG    Main         Denon: Got: CVSB 50 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,539 DEBUG    Main         Denon: Got: CVFHL 50 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,580 DEBUG    Main         Denon: Got: CVFHR 50 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,620 DEBUG    Main         Denon: Got: MVMAX 98 -- __init__.py:found_terminator:40
2014-01-07 17:26:50,662 DEBUG    Main         Denon: Got: SDAUTO -- __init__.py:found_terminator:40
2014-01-07 17:26:50,710 DEBUG    Main         Denon: Got: SVSOURCE -- __init__.py:found_terminator:40
2014-01-07 17:26:50,740 DEBUG    Main         Denon: Got: DCAUTO -- __init__.py:found_terminator:40
'''
