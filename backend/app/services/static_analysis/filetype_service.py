from pathlib import Path

import magic


class FileTypeService:
    @staticmethod
    def detect(path: Path) -> str:
        return magic.from_file(str(path), mime=True)
