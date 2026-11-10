import json
import os
import platform
import sys
from pathlib import Path

from assistant.app.logger import logger
from assistant.utils.resolve import USR_CONFIG_PATH

ENVIRONMENT_PATH = USR_CONFIG_PATH.parent / "environment.json"

# Seuls ces champs déclenchent une mise à jour ; le nom de machine est informatif.
COMPARED_KEYS = ("machine_id", "drive_letter", "volume_label", "volume_serial")


class EnvironmentService:
    """Détecte un changement de machine ou de disque racine depuis la dernière mise à jour."""

    def __init__(self, root_path: Path, state_path: Path = ENVIRONMENT_PATH):
        self.root_path = Path(root_path)
        self.state_path = state_path

    @staticmethod
    def _machine_id() -> str | None:
        try:
            if sys.platform == "win32":
                import winreg
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Cryptography",
                    0,
                    winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
                ) as key:
                    return str(winreg.QueryValueEx(key, "MachineGuid")[0])
            for candidate in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
                if os.path.exists(candidate):
                    return Path(candidate).read_text(encoding="utf8").strip()
        except OSError as exc:
            logger.warning("Identifiant machine illisible : %s", exc)
        return None

    @staticmethod
    def _volume_info(anchor: str) -> tuple[str | None, str | None]:
        """Retourne (nom du volume, numéro de série) ; (None, None) hors Windows."""
        if sys.platform != "win32":
            return None, None
        import ctypes
        label = ctypes.create_unicode_buffer(261)
        serial = ctypes.c_uint32(0)
        ok = ctypes.windll.kernel32.GetVolumeInformationW(  # type: ignore[attr-defined]
            ctypes.c_wchar_p(anchor), label, len(label),
            ctypes.byref(serial), None, None, None, 0,
        )
        if not ok:
            logger.warning("Informations du volume %s illisibles", anchor)
            return None, None
        return label.value, f"{serial.value:08X}"

    def current_fingerprint(self) -> dict[str, str | None]:
        anchor = self.root_path.resolve().anchor
        label, serial = self._volume_info(anchor)
        return {
            "machine_id": self._machine_id(),
            "machine_name": platform.node(),
            "drive_letter": anchor,
            "volume_label": label,
            "volume_serial": serial,
        }

    def load_saved(self) -> dict | None:
        try:
            with open(self.state_path, encoding="utf8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return None
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Fichier d'environnement illisible : %s", exc)
            return None
        return data if isinstance(data, dict) else None

    def update_needed(self, current: dict | None = None) -> bool:
        """Vrai si aucun état mémorisé n'existe ou si machine/disque ont changé."""
        current = current or self.current_fingerprint()
        saved = self.load_saved()
        if saved is None:
            logger.info("Aucun environnement mémorisé : mise à jour nécessaire")
            return True
        changed = [k for k in COMPARED_KEYS if saved.get(k) != current.get(k)]
        if changed:
            logger.info("Environnement modifié (%s) : mise à jour nécessaire", ", ".join(changed))
        return bool(changed)

    def save(self, fingerprint: dict | None = None) -> None:
        fingerprint = fingerprint or self.current_fingerprint()
        tmp_path = self.state_path.with_suffix(".tmp")
        try:
            with open(tmp_path, "w", encoding="utf8") as f:
                json.dump(fingerprint, f, indent=4, ensure_ascii=False)
            os.replace(tmp_path, self.state_path)
        except OSError as exc:
            logger.error("Impossible de mémoriser l'environnement : %s", exc)
