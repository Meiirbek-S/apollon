from pathlib import Path

import yara


class YaraService:
    def __init__(self, rules_path: str = "rules/yara/main.yar") -> None:
        self.rules = yara.compile(rules_path)

    def scan(self, path: Path) -> list[dict]:
        matches = self.rules.match(str(path))
        return [{"rule": m.rule, "tags": m.tags} for m in matches]
