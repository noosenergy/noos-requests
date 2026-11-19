"""TLS helpers for HTTP clients.

Requires the `pkcs12` extra: `pip install noos-pyk[pkcs12]`.
"""

import datetime as dt
import secrets

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12


def load_pkcs12_cert(data: bytes, password: str | bytes | None = None) -> tuple[str, str, str]:
    """Convert a PKCS#12 bundle into a client certificate usable by `niquests`.

    The result is meant to be assigned to `niquests.Session.cert`, which accepts in-memory
    PEM data as a `(certificate, key, key_password)` tuple.

    Args:
        data: Content of the PKCS#12 bundle.
        password: Password of the bundle, or None when it has none.

    Returns:
        The PEM certificate chain, the PEM private key encrypted with a random password,
        and that password.

    Raises:
        ValueError: If the bundle misses a private key or a certificate, or if any of its
            certificates is expired.
    """
    if isinstance(password, str):
        password = password.encode("utf-8")

    private_key, certificate, extra_certs = pkcs12.load_key_and_certificates(data, password)
    if private_key is None or certificate is None:
        raise ValueError("PKCS#12 bundle is missing a private key or certificate.")

    chain = [certificate, *(extra_certs or [])]
    for cert in chain:
        _reject_expired_certificate(cert)

    key_password = secrets.token_urlsafe(16)
    key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(key_password.encode("utf-8")),
    )
    cert_pem = b"".join(cert.public_bytes(serialization.Encoding.PEM) for cert in chain)
    return cert_pem.decode("ascii"), key_pem.decode("ascii"), key_password


def _reject_expired_certificate(certificate: x509.Certificate) -> None:
    expires_at = certificate.not_valid_after_utc
    if expires_at < dt.datetime.now(dt.UTC):
        raise ValueError(f"Client certificate expired: Not After: {expires_at:%Y-%m-%d %H:%M:%SZ}")
