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

import socket
from time import time
from pathlib import Path


def check_connection(host: str, port: int) -> bool:
    try:
        address = (host, port)
        socket.create_connection(address)
        return True
    except socket.error as err:
        print(err)
        return False


def is_valid_cache(cache_path: Path, expiration: int = 3600) -> bool:
    return cache_path and cache_path.is_file() and time() - \
        cache_path.stat().st_mtime < expiration
