#-----------------------------------------------------------------------------
# Copyright (c) 2013-2016, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------


"""
Import hook for PyEnchant.

Tested with PyEnchatn 1.6.6.
"""

import os
import sys

from PyInstaller.compat import is_darwin
from PyInstaller.utils.hooks import exec_statement, collect_data_files, \
    collect_dynamic_libs, eval_script


# TODO Add Linux support
# Collect first all files that were installed directly into pyenchant
# package directory and this includes:
# - Windows: libenchat-1.dll, libenchat_ispell.dll, libenchant_myspell.dll, other
#            dependent dlls and dictionaries for several languages (de, en, fr)
# - Mac OS X: usually libenchant.dylib and several dictionaries when installed via pip.
binaries = collect_dynamic_libs('enchant')
datas = collect_data_files('enchant')
excludedimports = ['enchant.tests']

# On OS X try to find files from Homebrew or Macports environments.
if is_darwin:
    # Note: env. var. ENCHANT_PREFIX_DIR is implemented only in the development version:
    #    https://github.com/AbiWord/enchant
    #    https://github.com/AbiWord/enchant/pull/2
    # TODO Test this hook with development version of enchant.
    libenchant = exec_statement("""
from enchant._enchant import e
print(e._name)
""").strip()

    # Check libenchant was not installed via pip but is somewhere on disk.
    # Probably it was installed from Homebrew or Macports.
    if not libenchant.startswith(sys.prefix):
        # 'libenchant' was not installed via pip.
        # Note: Name of detected enchant library is 'libenchant.dylib'. However, it
        #       is just symlink to 'libenchant.1.dylib'.
        binaries.append((libenchant, ''))

        # Collect enchant backends from Macports. Using same file structure as on Windows.
        backends = exec_statement("""
from enchant import Broker
for provider in Broker().describe():
    print(provider.file)""").strip().split()
        binaries.extend([(b, 'enchant/lib/enchant') for b in backends])

        # Collect all available dictionaries from Macports. Using same file structure as on Windows.
        # In Macports are available mostly hunspell (myspell) and aspell dictionaries.
        libdir = os.path.dirname(libenchant)  # e.g. /opt/local/lib
        sharedir = os.path.join(os.path.dirname(libdir), 'share')  # e.g. /opt/local/share
        datas.append((os.path.join(sharedir, 'enchant'), 'enchant/share/enchant'))
        datas.append((os.path.join(sharedir, 'hunspell'), 'enchant/share/enchant/hunspell'))
        datas.append((os.path.join(sharedir, 'aspell'), 'enchant/share/enchant/aspell'))
