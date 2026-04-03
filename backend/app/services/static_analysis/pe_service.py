from pathlib import Path

import pefile


class PEService:
    @staticmethod
    def analyze(path: Path) -> dict:
        pe = pefile.PE(str(path), fast_load=True)
        pe.parse_data_directories()

        sections = []
        for section in pe.sections:
            sections.append(
                {
                    "name": section.Name.decode(errors="ignore").strip("\x00"),
                    "entropy": section.get_entropy(),
                    "virtual_size": section.Misc_VirtualSize,
                    "raw_size": section.SizeOfRawData,
                }
            )

        imports: list[str] = []
        if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                for imp in entry.imports:
                    if imp.name:
                        imports.append(imp.name.decode(errors="ignore"))

        return {
            "machine": pe.FILE_HEADER.Machine,
            "timestamp": pe.FILE_HEADER.TimeDateStamp,
            "sections": sections,
            "imports": imports,
        }
