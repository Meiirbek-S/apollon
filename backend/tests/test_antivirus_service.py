import unittest

from app.services.antivirus import EICAR_MD5, scan_file_with_antivirus_bases


class AntivirusServiceTests(unittest.TestCase):
    def test_eicar_has_detected_entries(self) -> None:
        result = scan_file_with_antivirus_bases(
            sha256="".join(["a" for _ in range(64)]),
            md5=EICAR_MD5,
        )
        detected = [item for item in result if item["status"] == "detected"]
        self.assertGreater(len(detected), 10)
        kaspersky = next(item for item in result if item["engine"] == "Kaspersky")
        self.assertTrue(kaspersky["detected"])

    def test_non_eicar_mostly_undetected(self) -> None:
        result = scan_file_with_antivirus_bases(
            sha256="".join(["b" for _ in range(64)]),
            md5="".join(["0" for _ in range(32)]),
        )
        statuses = {item["status"] for item in result}
        self.assertIn("undetected", statuses)
        self.assertNotIn("detected", statuses)


if __name__ == "__main__":
    unittest.main()
