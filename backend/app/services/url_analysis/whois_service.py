from datetime import datetime, timezone

import whois


class WhoisService:
    @staticmethod
    def get_info(domain: str) -> dict:
        data = whois.whois(domain)
        creation_date = data.creation_date
        if isinstance(creation_date, list) and creation_date:
            creation_date = creation_date[0]

        age_days = None
        if isinstance(creation_date, datetime):
            age_days = (datetime.now(timezone.utc) - creation_date.replace(tzinfo=timezone.utc)).days

        return {
            "registrar": data.registrar,
            "creation_date": str(creation_date) if creation_date else None,
            "age_days": age_days,
        }
