import hashlib
from pathlib import Path


class HashService:
    @staticmethod
    def calculate_from_bytes(data: bytes) -> dict[str, str]:
        return {
            "sha256": hashlib.sha256(data).hexdigest(),
            "md5": hashlib.md5(data).hexdigest(),
        }

    @staticmethod
    def calculate_from_file(path: Path) -> dict[str, str]:
        digest_md5 = hashlib.md5()
        digest_sha = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(8192), b""):
                digest_md5.update(chunk)
                digest_sha.update(chunk)
        return {"sha256": digest_sha.hexdigest(), "md5": digest_md5.hexdigest()}
