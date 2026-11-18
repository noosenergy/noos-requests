import datetime as dt

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12

from noos_pyk.clients import tls


VALID_UNTIL = dt.datetime(2099, 1, 1, tzinfo=dt.UTC)
EXPIRED_AT = dt.datetime(2020, 1, 1, tzinfo=dt.UTC)


def _certificate(key: rsa.RSAPrivateKey, name: str, not_after: dt.datetime) -> x509.Certificate:
    subject = x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, name)])
    return (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(dt.datetime(2019, 1, 1, tzinfo=dt.UTC))
        .not_valid_after(not_after)
        .sign(key, hashes.SHA256())
    )


def _bundle(
    *,
    not_after: dt.datetime = VALID_UNTIL,
    ca_not_after: dt.datetime | None = None,
    with_key: bool = True,
) -> bytes:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    cas = [_certificate(key, "ca", ca_not_after)] if ca_not_after else None
    return pkcs12.serialize_key_and_certificates(
        name=b"test",
        key=key if with_key else None,
        cert=_certificate(key, "leaf", not_after),
        cas=cas,
        encryption_algorithm=serialization.BestAvailableEncryption(b"secret"),
    )


class TestLoadPkcs12Cert:
    @pytest.mark.parametrize("password", ["secret", b"secret"])
    def test_returns_pem_certificate_and_encrypted_key(self, password):
        cert_pem, key_pem, key_password = tls.load_pkcs12_cert(_bundle(), password)

        assert cert_pem.count("-----BEGIN CERTIFICATE-----") == 1
        assert key_pem.startswith("-----BEGIN ENCRYPTED PRIVATE KEY-----")
        serialization.load_pem_private_key(key_pem.encode(), key_password.encode())

    def test_includes_the_certificate_chain(self):
        cert_pem, _, _ = tls.load_pkcs12_cert(_bundle(ca_not_after=VALID_UNTIL), "secret")

        assert cert_pem.count("-----BEGIN CERTIFICATE-----") == 2

    def test_rejects_missing_private_key(self):
        with pytest.raises(ValueError, match="missing a private key or certificate"):
            tls.load_pkcs12_cert(_bundle(with_key=False), "secret")

    @pytest.mark.parametrize(
        "bundle_kwargs",
        [{"not_after": EXPIRED_AT}, {"ca_not_after": EXPIRED_AT}],
        ids=["leaf", "chain"],
    )
    def test_rejects_expired_certificate(self, bundle_kwargs):
        with pytest.raises(ValueError, match="Client certificate expired"):
            tls.load_pkcs12_cert(_bundle(**bundle_kwargs), "secret")
