# (void)walker GDB backend
# Copyright (C) 2012 David Holm <dholmster@gmail.com>

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

import gdb
import os.path
import re

from ..platform.architecture import ArchitectureManager
from ..platform.cpu import Architecture
from ..target.factory import TargetFactory
from ..target.inferior import Inferior
from ..target.thread import Thread
from ..utils.decorators import singleton_implementation


class GdbThread(Thread):
    def __init__(self, inferior_id, gdb_thread):
        super(GdbThread, self).__init__(inferior_id)
        self._gdb_thread = gdb_thread

    def name(self):
        return self._gdb_thread.name

    def id(self):
        return self._gdb_thread.num

    def is_valid(self):
        return self._gdb_thread.is_valid()


class GdbInferior(Inferior):
    def __init__(self, cpu, gdb_inferior):
        super(GdbInferior, self).__init__(cpu)
        self._gdb_inferior = gdb_inferior

    def id(self):
        return self._gdb_inferior.num

    def gdb_inferior(self):
        return self._gdb_inferior

    def read_memory(self, address, length):
        return self._gdb_inferior.read_memory(address, length)


@singleton_implementation(TargetFactory)
class GdbTargetFactory(object):
    _file_expression = re.compile((r'`(?P<path>[^\']+)\', '
                                   r'file type (?P<target>\S+).'))
    _inferior_expression = re.compile((r'(?P<num>\d+)\s+'
                                       r'(?P<description>\S+ \S*)\s+'
                                       r'(?P<path>.+)$'))

    def __init__(self):
        pass

    @staticmethod
    def _target_to_architecture(target):
        if re.match(r'.*-x86-64', target):
            return Architecture.X86_64
        if re.match(r'.*-i386', target):
            return Architecture.X86
        if re.match(r'.*-.*mips[^-]*', target):
            return Architecture.MIPS
        if re.match(r'.*-arm[^-]*', target):
            return Architecture.ARM
        return None

    def create_inferior(self, inferior_id):
        gdb_inferior = None
        try:
            gdb_inferior = (i for i in gdb.inferiors()
                            if i.num == inferior_id).next()
        except StopIteration:
            return None

        cpu = None
        info_inferiors = gdb.execute('info inferiors', False, True)
        info_target = gdb.execute('info target', False, True)
        try:
            matches = self._inferior_expression.findall(info_inferiors)
            inferior = (i for i in matches if int(i[0]) == inferior_id).next()

            inferior_path = os.path.abspath(inferior[2]).strip()
            matches = self._file_expression.findall(info_target)
            target = (i[1] for i in matches
                      if os.path.abspath(i[0]).strip() == inferior_path).next()

            architecture = self._target_to_architecture(target)
            cpu = ArchitectureManager().create_cpu(architecture)

        except TypeError:
            return None

        return GdbInferior(cpu, gdb_inferior)

    def create_thread(self, inferior, thread_id):
        gdb_thread = None
        try:
            gdb_thread = (i for i in inferior.gdb_inferior().threads()
                          if i.num == thread_id).next()
            thread = GdbThread(inferior.id(), gdb_thread)
            inferior.add_thread(thread)
            return thread

        except StopIteration:
            pass

        return None
