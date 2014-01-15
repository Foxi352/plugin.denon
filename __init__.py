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
import threading

from time import sleep

import lib.connection

logger = logging.getLogger('Denon')


class Denon(lib.connection.Client):

    # Initialize connection to receiver
    def __init__(self, smarthome, host, port=23, cycle=15):
        logger.info("Denon: connecting to {0}:{1}".format(host, port))
        lib.connection.Client.__init__(self, host, port, monitor=True)
        self.terminator = b'\r'
        self._host = host
        self._sh = smarthome
        self._items = {}
        self._sources = {}
        self._cmd_lock = threading.Lock()
        self._status_objects = ['SI?', 'MU?', 'PSBAS ?', 'PSTRE ?']
        self._status_objects_count = len(self._status_objects)
        self._status_objects_pointer = 0

        # After power on poll status objects
        self._sh.scheduler.add('status-update', self._update_status, cycle=5)
        self._sh.scheduler.change('status-update', active=False)

        # Sadly the Denon does not send an event on now playing change
        self._sh.scheduler.add('nowplaying-update', self._update_now_playing, cycle=cycle)
        self._sh.scheduler.change('nowplaying-update', active=False)

    # On connect poll states
    def handle_connect(self):
        self._send('PW?')

    # Parse received input from Denon and set items
    def found_terminator(self, data):
        data = data.decode()
        logger.debug("Denon: Got: {0} from {1}".format(data, self._host))
        # AVR switched on
        if data == 'PWON':
            logger.info("Denon: {0} powered on".format(self._host))
            self._items['power'](True, 'Denon', self._host)
            sleep(1.5)
            self._send('MV?')
            self._sh.scheduler.change('status-update', active=True)
        # AVR entered standby
        elif data == 'PWSTANDBY':
            logger.info("Denon: {0} powered off".format(self._host))
            self._items['power'](False, 'Denon', self._host)
            self._sh.scheduler.change('status-update', active=False)
        # AVR is muted
        elif data == 'MUON':
            logger.info("Denon: {0} muted".format(self._host))
            self._items['mute'](True, 'Denon', self._host)
        # AVE is unmuted
        elif data == 'MUOFF':
            logger.info("Denon: {0} unmuted".format(self._host))
            self._items['mute'](False, 'Denon', self._host)
        # Got master volume
        elif data.startswith('MV'):
            #self._send('PSBAS ?')
            #self._send('PSTRE ?')
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
        # Got BASS setting
        elif data.startswith('PSBAS'):
            try:
                # 3 digits volume means last digit is decimal. Cut it ! :-)
                bass = data[6:]
                if bass.isdigit():
                    logger.info("Denon: {0} bass setting is {1}".format(self._host, bass))
                    self._items['bass'](bass, 'Denon', self._host)
                else:
                    logger.debug("Denon: Unknown BASS info received")
            except:
                logger.debug("Denon: Unknown BASS info received")
        # Got TREBBLE setting
        elif data.startswith('PSTRE'):
            try:
                # 3 digits volume means last digit is decimal. Cut it ! :-)
                trebble = data[6:]
                if trebble.isdigit():
                    logger.info("Denon: {0} trebble setting is {1}".format(self._host, trebble))
                    self._items['trebble'](trebble, 'Denon', self._host)
                else:
                    logger.debug("Denon: Unknown TREBBLE info received")
            except:
                logger.debug("Denon: Unknown TREBBLE info received")
        # Got onscreen display info containing title and artist now playing
        elif data.startswith('NSE'):
            try:
                line = data[3:][:1]
                if line.isdigit():
                    line = int(line)
                    if line == 0:
                        content = data[4:]
                    elif line == 1:
                        content = data[5:]
                    else:
                        content = data[6:]
                    if content:
                        # Now playing
                        if line == 1:
                            logger.info("Denon: {} Now playing {}".format(self._host, content))
                            self._items['title'](content, 'Denon', self._host)
                        # Internet radio Station name
                        elif line == 2 and self._items['source']() == 'IRADIO':
                            logger.info("Denon: {} Internet radio station {}".format(self._host, content))
                            self._items['station'](content, 'Denon', self._host)
                else:
                    logger.debug("Denon: Unknown display line info received")
            except:
                logger.debug("Denon: Unknown display line info received")
        # Got input source information
        elif data.startswith('SI'):
            source = data[2:]
            logger.info("Denon: {0} source is {1}".format(self._host, source))
            self._items['source'](source, 'Denon', self._host)
            # If source is internet radio, poll nowplaying (display lines) regularly
            if source == 'IRADIO':
                self._sh.scheduler.change('nowplaying-update', active=True)
                self._sh.trigger('nowplaying-update', self._update_now_playing)
            else:
                self._sh.scheduler.change('nowplaying-update', active=False)
                self._items['title']('', 'Denon', self._host)
                self._items['station']('', 'Denon', self._host)

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
        elif 'denon_listen' in item.conf:
            info = item.conf['denon_listen']
            if (info is None):
                return None
            else:
                self._items[info] = item
                logger.debug("Denon: Listening to {} info".format(info))
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

    # Poll for now playing updates
    def _update_status(self):
        self._send(self._status_objects[self._status_objects_pointer])
        self._status_objects_pointer += 1
        if self._status_objects_pointer >= self._status_objects_count:
            self._status_objects_pointer = 0

    # Poll for now playing updates
    def _update_now_playing(self):
        self._send('NSE')

    # Send commands to receiver if connected
    def _send(self, cmd):
        self._cmd_lock.acquire()
        if not self.connected:
            logger.warning("Denon: No connection, can not send command: {0}".format(cmd))
            return
        logger.debug("Denon: Sending request: {0}".format(cmd))
        self.send(bytes(cmd + '\r', 'utf-8'))
        self._cmd_lock.release()
