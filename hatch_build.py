import logging
import platform
from pathlib import Path
from typing import Callable, override
from zipfile import ZIP_DEFLATED, ZipFile

from hatchling.builders.plugin.interface import BuilderInterface
from PyInstaller.__main__ import run as pyinstaller_run

logger = logging.getLogger("hatch_pyinstaller_builder")
logger.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
logger.addHandler(stdoutHandler)


class PyInstallerBuilder(BuilderInterface):
    PLUGIN_NAME = "pyinstaller"

    @override
    def get_version_api(self) -> dict[str, Callable]:
        return {"v1": self.build_pyinstaller}

    def build_pyinstaller(self, build_dir: str, **build_data: dict) -> str:
        project_name = self.normalize_file_name_component(self.metadata.name)

        # Get pyinstaller spec if available otherwise fallback to the main project script (save_converter.py)
        installer_spec = self.target_config.get("pyinstaller_spec", f"{project_name}.py")
        spec_path = Path(installer_spec)
        if not spec_path.exists():
            logger.error(
                f"Pyinstaller spec file or python script file at path {spec_path} does not exist. Nothing to build..."
            )
            return ""

        # dist dir can be hatch's dist path or pyinstaller option distpath.
        dist_dir: Path = Path(self.target_config.get("distpath", build_dir))
        dist_dir.mkdir(parents=True, exist_ok=True)
        dist_path = dist_dir / project_name
        self.target_config["distpath"] = str(dist_path)

        # Construct pyinstaller arguments - to do only once all coherency checks are done
        installer_args: list[str] = [str(spec_path), "--noconfirm", "--distpath", str(dist_dir)]

        pyinstaller_run(installer_args)

        # When true zip, stores installer artifacts into a zip file
        result_path = dist_path
        if self.target_config.get("zip", True):
            dest_zip_path = dist_dir / (
                f"{project_name}-{self.metadata.version}-{platform.system()}-{platform.machine()}.zip"
            )
            result_path = dest_zip_path
            with ZipFile(dest_zip_path, mode="w", compression=ZIP_DEFLATED) as zipfile:
                for dirpath, _dirnames, filenames in dist_path.walk(top_down=False):
                    for filename in filenames:
                        dest_srcname = dirpath / filename
                        dest_arcname = dest_srcname.relative_to(dist_path)
                        zipfile.write(filename=dest_srcname, arcname=dest_arcname)

        return str(result_path)
