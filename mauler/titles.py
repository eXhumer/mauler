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

import re
import os
import json
import logging
from time import time
from pathlib import Path
from mauler import config

__titles = {}
__titles_path = Path('conf/titles.json')


class Title:
    __path = None
    __title_id = None
    __version = None

    def __init__(self, path: Path = None):
        self.path = path

    @property
    def path(self):
        return str(self.__path)

    @path.setter
    def path(self, val: Path):
        self.__path = val

        if val and val.is_file():
            check_title_id = re.match(r'.*\[(?P<title_id>[a-fA-F0-9]{16})\].*',
                                      str(val), re.I)

            if check_title_id:
                self.title_id = check_title_id.group('title_id')

            check_version = re.match(r'.*\[v(?P<version>[0-9]+)\].*', str(val),
                                     re.I)

            if check_version:
                self.version = int(check_version.group('version'))
            else:
                self.version = 0

    @property
    def title_id(self):
        return self.__title_id or ('0' * 16)

    @title_id.setter
    def title_id(self, val: str):
        if not re.match(r'[A-F0-9]{16}', val, re.I):
            logging.warning('Title ID specified is not a valid title ID. ' +
                            'Valid Title ID must be a 16 characters ' +
                            'hexadecimal string!')
        self.__title_id = val

    @property
    def version(self):
        return self.__version

    @version.setter
    def version(self, val: int):
        self.__version = val

    @property
    def info(self):
        return {
            'title_id': self.title_id,
            'version': self.version,
            'path': str(self.path)
        }

    @property
    def file_name(self):
        return self.__path.name


def get_all_title_ids():
    return [title.title_id for title in __titles.values()]


def get_title(path):
    return __titles[path]


def get_title_by_title_id(title_id):
    for title in __titles.values():
        if title.title_id == title_id:
            return title

    return None


def is_title_available(title_id):
    return title_id in __titles


def get_base_id(title_id):
    return '{:016X}'.format(int(title_id, 16) & 0xFFFFFFFFFFFFE000)


def get_update_id(title_id):
    return get_base_id(title_id)[:13] + '800'


def is_base(title_id):
    return get_base_id(title_id).lower() == title_id.lower()


def is_update(title_id):
    return get_update_id(title_id) == title_id


def is_dlc(title_id):
    return not is_base(title_id) and not is_update(title_id)


def scan(base):
    global __titles

    scan_count = 0
    title_list = {}

    logging.info(f'scanning files in {base}')

    for root, dirs, file_names in os.walk(base, topdown=False,
                                          followlinks=True):
        root_path = Path(root)
        for file_name in file_names:
            file_path = root_path.joinpath(file_name).resolve()

            if file_path.suffix in config.paths.title_exts:
                title_list[str(file_path)] = file_name

    if len(title_list) == 0:
        __save()
        return 0

    for path, file_name in title_list.items():
        if path not in __titles:
            _path = Path(path)
            logging.info(f'adding {file_name}')
            __titles[path] = Title(_path)

            scan_count = scan_count + 1
            if scan_count % 20 == 0:
                __save()

    __save()
    return scan_count


def __load():
    global __titles

    timestamp = time()

    with __titles_path.open(mode='r', encoding='utf8') as titles_stream:
        for _title in json.load(titles_stream):
            title = Title(None)
            title.path = Path(_title['path'])
            title.title_id = _title['title_id']
            title.version = _title['version']

            if not title.path:
                continue

            title_path = Path(title.path).resolve()

            if title_path.is_file():
                __titles[title.path] = title

    logging.info(f'loaded file list in {time() - timestamp} seconds')


def __save():
    __titles_path.parent.mkdir(exist_ok=True, parents=True)

    titles = []

    if __titles_path.is_file():
        with __titles_path.open(mode='r', encoding='utf8') as titles_stream:
            titles = titles + json.load(titles_stream)

    for _, title in __titles.items():
        titles.append(title.info)

    with __titles_path.open(mode='w', encoding='utf8') as titles_stream:
        json.dump(titles, titles_stream, indent=4, sort_keys=True)


for scan_str in config.paths.scan:
    scan(scan_str)


if __titles_path.is_file():
    __load()
