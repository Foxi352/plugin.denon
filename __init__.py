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
from time import sleep

import lib.connection

logger = logging.getLogger('Denon')


class Denon(lib.connection.Client):

    # Initialize connection to receiver
    def __init__(self, smarthome, host, port=23):
        logger.info("Denon: connecting to {0}:{1}".format(host, port))
        lib.connection.Client.__init__(self, host, port, monitor=True)
        self.terminator = b'\r'
        self._host = host
        self._sh = smarthome
        self._items = {}

    # On connect poll states
    def handle_connect(self):
        self._send('PW?')
        sleep(0.2)
        self._send('MU?')

    # Parse received input from Denon and set items
    def found_terminator(self, data):
        data = data.decode()
        logger.debug("Denon: Got: {0} from {1}".format(data, self._host))
        if data == 'PWON':
            logger.info("Denon: {0} powered on".format(self._host))
            self._items['power'](True, 'Denon', self._host)
            self._send('MV?')
            self._send('SI?')
        elif data == 'PWSTANDBY':
            logger.info("Denon: {0} powered off".format(self._host))
            self._items['power'](False, 'Denon', self._host)
        elif data == 'MUON':
            logger.info("Denon: {0} muted".format(self._host))
            self._items['mute'](True, 'Denon', self._host)
        elif data == 'MUOFF':
            logger.info("Denon: {0} unmuted".format(self._host))
            self._items['mute'](False, 'Denon', self._host)
        elif data.startswith('MV'):
            try:
                # 3 digits volume means last digit is decimal. Cut it ! :-)
                vol = data[2:][:2]
                if vol.isdigit():
                    logger.info("Denon: {0} is at volume {1}".format(self._host, vol))
                    self._items['volume'](vol, 'Denon', self._host)
                else:
                    logger.debug("Denon: Unknown volume info received")
            except:
                logger.debug("Denon: Unknown volume info received")
        elif data.startswith('SI'):
             source = data[2:]
             logger.info("Denon: {0} source is {1}".format(self._host, source))
             self._items['source'](source, 'Denon', self._host)

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
            else:
                self._items[cmd] = item
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
                elif(command == 'mute') and (isinstance(value, bool)):
                    self._send('MUON' if value else 'MUOFF')
                elif(command == 'volume') and (isinstance(value, int)):
                    self._send('MV{0}'.format(value))
                elif(command == 'volume+'):
                    self._send('MVUP')
                elif(command == 'volume-'):
                    self._send('MVDOWN')
                elif(command == 'source'):
                    self._send('SI{}'.format(value))
                else:
                    logger.warning("Denon: Command {0} or value {1} invalid".format(command, value))

    # Send commands to receiver if connected
    def _send(self, cmd):
        if not self.connected:
            logger.warning("Denon: No connection, can not send command: {0}".format(cmd))
            return
        logger.debug("Denon: Sending request: {0}".format(cmd))
        self.send(bytes(cmd + '\r', 'utf-8'))
