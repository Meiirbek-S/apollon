import dns.resolver


class DnsService:
    @staticmethod
    def resolve(domain: str) -> dict[str, list[str]]:
        records: dict[str, list[str]] = {}
        for rtype in ("A", "AAAA", "MX", "NS"):
            try:
                answers = dns.resolver.resolve(domain, rtype)
                records[rtype] = [str(a) for a in answers]
            except Exception:
                records[rtype] = []
        return records
