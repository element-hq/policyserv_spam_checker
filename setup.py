#
# This file is licensed under the Affero General Public License (AGPL) version 3.
#
# Copyright (C) 2025 New Vector, Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# See the GNU Affero General Public License for more details:
# <https://www.gnu.org/licenses/agpl-3.0.html>.
#

from setuptools import setup, find_packages

setup(
    name="policy-server-checker",
    version="0.0.1",
    packages=find_packages(),
    description="MSC4284 Policy Server",
    include_package_data=True,
    zip_safe=True,
    install_requires=[],
)
