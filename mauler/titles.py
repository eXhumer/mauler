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
from pathlib import Path
from mauler import config

__titles = {}
__titles_path = Path('conf/titles.json')
TITLE_ID_PATTERN = r'.*\[(?P<title_id>[a-fA-F0-9]{16})\].*'
VERSION_PATTERN = r'.*\[v(?P<version>[0-9]+)\].*'


class Title:
    __path = None
    __title_id = None
    __version = None

    def __init__(self, path: Path):
        self.path = path

    @property
    def path_str(self):
        return str(self.__path) if self.__path else None

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, new_path: Path):
        self.__path = new_path

        if self.__path is not None:
            if self.__path.is_file():
                title_id_check = re.match(TITLE_ID_PATTERN, self.__path.name,
                                          re.I)

                if title_id_check:
                    self.title_id = title_id_check.group('title_id')

                    version_check = re.match(VERSION_PATTERN, new_path.name,
                                             re.I)

                    self.version = int(version_check.group('version')) if \
                        version_check else 0
                else:
                    self.__path = None
            else:
                self.__path = None

    @property
    def title_id(self):
        return self.__title_id

    @title_id.setter
    def title_id(self, new_title_id: str):
        self.__title_id = new_title_id.upper()

    @property
    def version(self):
        return self.__version

    @version.setter
    def version(self, val: int):
        self.__version = val

    @property
    def info(self):
        return {
            self.title_id: self.path_str
        }

    @property
    def file_name(self):
        return self.__path.name

    @property
    def file_modified(self):
        return self.__path.stat().st_mtime

    @property
    def base_title_id(self):
        return '{:016X}'.format(int(self.__title_id, 16) & 0xFFFFFFFFFFFFE000)

    @property
    def update_title_id(self):
        return self.base_title_id[:13] + '800'

    @property
    def is_base(self):
        return self.__title_id == self.base_title_id

    @property
    def is_update(self):
        return self.__title_id == self.update_title_id

    @property
    def is_dlc(self):
        return not self.is_base and not self.is_update


def is_valid_title_path(path_to_check: Path):
    return path_to_check.suffix in config.paths.title_exts and \
        re.match(TITLE_ID_PATTERN, path_to_check.name, re.I)


def get_all_title_ids():
    return __titles.keys()


def get_title(title_id: str) -> Title:
    return __titles.get(title_id, None)


def is_title_available(title_id) -> bool:
    return title_id in __titles


def scan(base: str):
    global __titles

    scanned_title_list = {}

    __remove_deleted_files()

    for root, dirs, file_names in os.walk(base, topdown=False,
                                          followlinks=True):
        root_path = Path(root)
        for file_name in file_names:
            file_path = root_path.joinpath(file_name).resolve()

            title = Title(file_path)

            if not title.path:
                continue

            title_already_present = title.title_id in __titles
            title_already_scanned = title.title_id in scanned_title_list
            scanned_title_mtime = title.file_modified

            if title_already_present and __titles[title.title_id].version \
                    > title.version:
                continue

            if title_already_present and scanned_title_mtime <= \
                    __titles[title.title_id].file_modified:
                continue

            if title_already_scanned and \
                    scanned_title_list[title.title_id].version > title.version:
                continue

            if title_already_scanned and scanned_title_mtime <= \
                    scanned_title_list[title.title_id].file_modified:
                continue

            scanned_title_list[title.title_id] = title

    if len(scanned_title_list) > 0:
        for title_id, title in scanned_title_list.items():
            __titles[title_id] = title

    __save()


def __load():
    global __titles

    __titles.clear()

    with __titles_path.open(mode='r', encoding='utf8') as titles_stream:
        for title_id, title_path in json.load(titles_stream).items():
            title = Title(Path(title_path))

            if not title.path:
                continue

            if title.path.is_file():
                __titles[title.title_id] = title

    __save()


def __save():
    __titles_path.parent.mkdir(exist_ok=True, parents=True)

    titles = {}

    for title_id, title in __titles.items():
        titles.update({title_id: title.path_str})

    with __titles_path.open(mode='w', encoding='utf8') as titles_stream:
        json.dump(titles, titles_stream, indent=4, sort_keys=True)


def __remove_deleted_files():
    global __titles

    refreshed_titles = {}

    for title_id, title in __titles.items():
        if __titles[title_id].path.is_file():
            refreshed_titles.update({title_id: title})

    __titles.clear()
    __titles.update(refreshed_titles)
    __save()


if __titles_path.is_file():
    __load()


for scan_str in config.paths.scan:
    scan(scan_str)
