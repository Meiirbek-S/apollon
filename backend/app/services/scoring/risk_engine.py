from dataclasses import dataclass


@dataclass
class RiskResult:
    total_score: int
    verdict: str
    breakdown: dict[str, int]


class RiskEngine:
    @staticmethod
    def classify(total_score: int, critical_dynamic_ioc: bool = False) -> str:
        if total_score >= 60:
            return "MALWARE-LIKE"
        if total_score >= 25 or critical_dynamic_ioc:
            return "SUSPICIOUS"
        return "SAFE"

    @classmethod
    def evaluate(cls, static_score: int = 0, dynamic_score: int = 0, url_score: int = 0, critical_dynamic_ioc: bool = False) -> RiskResult:
        total = static_score + dynamic_score + url_score
        verdict = cls.classify(total, critical_dynamic_ioc)
        return RiskResult(
            total_score=total,
            verdict=verdict,
            breakdown={"static": static_score, "dynamic": dynamic_score, "url": url_score},
        )
