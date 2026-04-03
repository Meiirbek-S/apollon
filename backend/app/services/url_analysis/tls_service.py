import socket
import ssl
from datetime import datetime, timezone


class TLSService:
    @staticmethod
    def inspect(hostname: str, port: int = 443) -> dict:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as wrapped:
                cert = wrapped.getpeercert()

        not_after = cert.get("notAfter")
        expires_in_days = None
        if not_after:
            dt = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
            expires_in_days = (dt - datetime.now(timezone.utc)).days

        return {
            "subject": cert.get("subject"),
            "issuer": cert.get("issuer"),
            "expires_in_days": expires_in_days,
        }
