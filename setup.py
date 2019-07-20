###############################################################################
#
#   Copyright 2018-2019 Telefónica
#
#   csv2avro is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from setuptools import find_packages, setup
import pruvi


setup(
    name='pruvi',
    version=pruvi.__version__,
    author='Félix Brezo (@febrezo)',
    description='Python3.6+ package to create proofs for certain parts of '
                'different types of documents using Merkle Trees.',
    url='https://github.com/febrezo/pruvi',
    include_package_data=True,
    license='GNU GPLv3+',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pruvi=pruvi.launcher:main',
        ],
    },
    install_requires=[
        'pydub',
        'pymerkle',
    ],
    dependency_links=[
        'git+git://github.com/febrezo/pymerkle/@pure-byte-hashing#egg=pymerkle'
    ],
)
