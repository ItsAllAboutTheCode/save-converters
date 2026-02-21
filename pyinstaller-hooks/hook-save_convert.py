"""Hook which is executed during the Analysis phase of PyInstaller.

This allow the path to entry point script to be available in order to look up the "save_convert" local package.

This is needed because the "save_convert" local package is dynamically imported which PyInstaller cannot known
when collecting module dependencies
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

hiddenimports = collect_submodules("save_convert")
datas = collect_data_files("save_convert")
# Append the README.md file to the list of data files
datas.append(("README.md", "."))
