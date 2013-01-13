# (void)walker command line interface
# Copyright (C) 2012-2013 David Holm <dholmster@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import abc


class Command(object):
    def __init__(self):
        self._inferior_repository = None
        self._target_factory = None
        self._config = None
        self._terminal = None

    def init(self, inferior_repository, platform_factory, target_factory,
             config, terminal):
        self._platform_factory = platform_factory
        self._inferior_repository = inferior_repository
        self._target_factory = target_factory
        self._config = config
        self._terminal = terminal


class PrefixCommand(Command):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute(self, *_):
        self._terminal.write('%(face-error)sAttempting to invoke an '
                             'incomplete command!\n')


class DataCommand(Command):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute(self, terminal, thread, argument):
        raise NotImplementedError


class StackCommand(Command):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute(self, terminal, thread, argument):
        raise NotImplementedError


class BreakpointCommand(Command):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute(self, terminal, inferior, argument):
        raise NotImplementedError


class SupportCommand(Command):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute(self, terminal, argument):
        raise NotImplementedError


class CommandFactory(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create(self, command_type):
        raise NotImplementedError


class CommandBuilder(object):
    def __init__(self, command_factory, inferior_repository, platform_factory,
                 target_factory, config, terminal):
        self.commands = {}
        for Cmd in _command_list:
            cmd = command_factory.create(Cmd, inferior_repository,
                                         platform_factory, target_factory,
                                         config, terminal)
            self.commands[Cmd.name()] = cmd

def register_command(cls):
    _command_list.append(cls)
    return cls

_command_list = []

