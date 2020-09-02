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
from requests import request
from mauler.utils import is_valid_cache
from mauler.titles import get_all_title_ids, get_title, get_base_id, \
    is_dlc, is_update

__updates = {}
__cache_versions_path = Path('cache/versions.json')


def __get_latest_version(title_id: str):
    check_id = title_id

    if is_update(title_id):
        check_id = get_base_id(title_id)

    try:
        return max([int(version) for version in __updates[check_id].keys()])
    except KeyError:
        return 0


def get_outdated():
    outdated = {}

    for title_id in get_all_title_ids():
        latest = __get_latest_version(title_id)
        available = 0

        if is_update(title_id):
            title_id = get_base_id(title_id)

            try:
                available = get_title(title_id).version
            except KeyError:
                pass

        elif is_dlc(title_id):
            available = get_title(title_id).version

        if title_id in outdated:
            continue

        if latest > available:
            outdated.update({title_id: {
                'latest': latest,
                'available': available,
            }})

    return outdated


def __load():
    global __updates

    if is_valid_cache(__cache_versions_path):
        __load_cache()
    else:
        res = request('GET', 'https://api.github.com/repos/blawar/titledb' +
                      '/contents/versions.json',
                      headers={'Accept': 'application/vnd.github.v3.raw'})
        if res.status_code == 200:
            __updates.update(res.json())
            __save_cache()


def __load_cache():
    global __updates

    with __cache_versions_path.open(mode='r', encoding='utf8') \
            as cache_versions_stream:
        __updates.update(json.load(cache_versions_stream))


def __save_cache():
    __cache_versions_path.parent.mkdir(exist_ok=True, parents=True)

    with __cache_versions_path.open(mode='w', encoding='utf8') \
            as cache_versions_stream:
        json.dump(__updates, cache_versions_stream)


__load()
