#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mauler - Shows outdated Nintendo Switch titles
# Copyright (C) 2020 eXhumer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
from pathlib import Path


class Paths:
    def __init__(self):
        self.scan = ['.']
        self.title_exts = ['.nsp', '.nsz', '.xci', '.xcz']


def __load():
    global paths

    with __conf_path.open(mode='r', encoding='utf8') as conf_stream:
        conf = json.load(conf_stream)

        try:
            paths.scan = conf['paths']['scan']
        except KeyError:
            pass

        if not isinstance(paths.scan, list):
            paths.scan = [paths.scan]

        try:
            paths.title_exts = conf['paths']['title_exts']
        except KeyError:
            pass

        if not isinstance(paths.title_exts, list):
            paths.title_exts = [paths.title_exts]


paths = Paths()
__conf_path = Path('conf/mauler.conf')

if __conf_path.is_file():
    __load()
