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
import logging
from pathlib import Path
from requests import request
from mauler.utils import is_valid_cache
from mauler.titles import get_all_title_ids, get_title, is_title_available

__updates = {}
__cache_versions_path = Path('cache/versions.json')


def get_latest_version(versions) -> int:
    return max([int(version) for version in versions])


def get_title_version_info(title_id: str):
    title = get_title(title_id)

    if title is None:
        return None

    res = {
        'available': title.version,
        'latest': title.version
    }

    dlc_with_update = title.is_dlc and title_id.lower() in __updates
    base_with_update = title.is_base and not \
        is_title_available(title.update_title_id) and title_id.lower() in \
        __updates
    update_with_update = title.is_update and title.base_title_id.lower() in \
        __updates

    if base_with_update or dlc_with_update or update_with_update:
        if base_with_update or dlc_with_update:
            versions = __updates[title_id.lower()].keys()

        elif update_with_update:
            versions = __updates[title.base_title_id.lower()].keys()

        res['latest'] = get_latest_version(versions)

    return res


def get_all_title_version_info():
    all_title_version_info = {}

    for title_id in get_all_title_ids():
        title_version_info = get_title_version_info(title_id)
        all_title_version_info.update({title_id: title_version_info})

    return all_title_version_info


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
        else:
            logging.warning('Failed to get latest versions.json!')


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
