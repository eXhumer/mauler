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
        self.scan = [Path('.').resolve()]
        self.title_exts = ['.nsp', '.nsz', '.xci', '.xcz']

    @property
    def dict_to_save(self):
        return {
            'scan': [str(path) for path in self.scan],
            'title_exts': self.title_exts
        }


def __load():
    global paths

    with __conf_path.open(mode='r', encoding='utf8') as conf_stream:
        conf = json.load(conf_stream)

        try:
            paths_scan = conf['paths']['scan']

            if not isinstance(paths_scan, list):
                paths_scan = [paths_scan]

            paths.scan.clear()

            for scan_str in paths_scan:
                scan_path = Path(scan_str).resolve()

                if scan_path.is_dir():
                    paths.scan.append(scan_path)

        except KeyError:
            pass

        try:
            paths.title_exts = conf['paths']['title_exts']

            if not isinstance(paths.title_exts, list):
                paths.title_exts = [paths.title_exts]

        except KeyError:
            pass


def save():
    __conf_path.parent.mkdir(exist_ok=True, parents=True)

    out_conf = {}
    out_conf.update({'paths': paths.dict_to_save})

    with __conf_path.open(mode='w', encoding='utf8') as conf_stream:
        json.dump(out_conf, conf_stream)


paths = Paths()
__conf_path = Path('conf/mauler.conf')

if __conf_path.is_file():
    __load()
