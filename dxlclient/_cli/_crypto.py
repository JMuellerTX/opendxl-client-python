# -*- coding: utf-8 -*-
###############################################################################
# Copyright (c) 2018 McAfee LLC - All Rights Reserved.
###############################################################################

"""
Helpers for crypto operations used by the cli tools - e.g., for creating
certificate requests and private keys
"""

from __future__ import absolute_import
import logging
import re

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from dxlclient import DxlUtils

logger = logging.getLogger(__name__)


def _bytes_to_unicode(obj):
    """
    Convert a non-`bytes` type object into a unicode string.

    :param obj: the object to convert
    :return: If the supplied `obj` is of type `bytes`, decode it into a unicode
        string. If the `obj` is anything else (including None), the original
        `obj` is returned. If the object is converted into a unicode string,
        the type would be `unicode` for Python 2.x or `str` for Python 3.x.
    """
    return obj.decode() if isinstance(obj, bytes) else obj


class X509Name(object):
    """
    Holder for an X.509 distinguished name, e.g., /C=US/CN=myname.
    """
    def __init__(self, common_name):
        """
        Constructor parameters:

        :param str common_name: Common Name (CN) attribute
        """
        self._common_name = common_name
        self._country_name = None
        self._state_or_province_name = None
        self._locality_name = None
        self._organization_name = None
        self._organizational_unit_name = None
        self._email_address = None

    @property
    def common_name(self):
        """
        Common Name (CN) attribute

        :rtype: str
        """
        return self._common_name

    @property
    def country_name(self):
        """
        Country (C) attribute

        :rtype: str
        """
        return self._country_name

    @country_name.setter
    def country_name(self, value):
        """
        Country (C) attribute to set

        :param str value: new name
        """
        self._country_name = value

    @property
    def state_or_province_name(self):
        """
        State or Province (ST) attribute

        :rtype: str
        """
        return self._state_or_province_name

    @state_or_province_name.setter
    def state_or_province_name(self, value):
        """
        State or Province (ST) attribute to set

        :param str value: new name
        """
        self._state_or_province_name = value

    @property
    def locality_name(self):
        """
        Locality (C) attribute

        :rtype: str
        """
        return self._locality_name

    @locality_name.setter
    def locality_name(self, value):
        """
        Locality (L) attribute to set

        :param str value: new name
        """
        self._locality_name = value

    @property
    def organization_name(self):
        """
        Organization (O) attribute

        :rtype: str
        """
        return self._organization_name

    @organization_name.setter
    def organization_name(self, value):
        """
         Organization (O) attribute to set

         :param str value: new name
         """
        self._organization_name = value

    @property
    def organizational_unit_name(self):
        """
        Organizational Unit (OU) attribute

        :rtype: str
        """
        return self._organizational_unit_name

    @organizational_unit_name.setter
    def organizational_unit_name(self, value):
        """
         Organizational Unit (OU) attribute to set

         :param str value: new name
         """
        self._organizational_unit_name = value

    @property
    def email_address(self):
        """
        e-mail address attribute

        :rtype: str
        """
        return self._email_address

    @email_address.setter
    def email_address(self, value):
        """
         e-mail address attribute to set

         :param str value: new name
         """
        self._email_address = value


# The digest used for the certificate request signature (SHA-256, as before)
_CRYPTO_SIGN_DIGEST = hashes.SHA256()
_CRYPTO_KEY_TYPE = "rsa"
_CRYPTO_KEY_BITS = 2048
_CRYPTO_EC_CURVE = "secp256r1"

KEY_TYPES = ("rsa", "ec")
"""Supported private key types for certificate requests"""
RSA_KEY_SIZES = (2048, 3072, 4096)
"""Supported RSA key sizes in bits"""
EC_CURVES = ("secp256r1", "secp384r1", "secp521r1")
"""Supported named curves for EC keys"""

_EC_CURVE_CLASSES = {
    "secp256r1": ec.SECP256R1,
    "secp384r1": ec.SECP384R1,
    "secp521r1": ec.SECP521R1
}

# The order in which the attributes appear in the subject of the certificate
# request. It is the order the previous asn1crypto based implementation
# produced, so certificate requests keep the same subject string.
_SUBJECT_ATTRIBUTES = (
    ("country_name", NameOID.COUNTRY_NAME),
    ("state_or_province_name", NameOID.STATE_OR_PROVINCE_NAME),
    ("locality_name", NameOID.LOCALITY_NAME),
    ("organization_name", NameOID.ORGANIZATION_NAME),
    ("organizational_unit_name", NameOID.ORGANIZATIONAL_UNIT_NAME),
    ("common_name", NameOID.COMMON_NAME),
    ("email_address", NameOID.EMAIL_ADDRESS)
)


class _KeyPair(object):
    """
    RSA or EC private key generator
    """
    def __init__(self, key_type=_CRYPTO_KEY_TYPE, key_bits=_CRYPTO_KEY_BITS,
                 curve=_CRYPTO_EC_CURVE):
        """
        Constructor parameters:

        :param str key_type: ``"rsa"`` (default) or ``"ec"``
        :param int key_bits: RSA key size in bits (2048, 3072 or 4096)
        :param str curve: named curve for EC keys (secp256r1, secp384r1,
            secp521r1)
        """
        if key_type not in KEY_TYPES:
            raise ValueError("Unsupported key type: {}".format(key_type))
        if key_type == "ec":
            if curve not in EC_CURVES:
                raise ValueError("Unsupported EC curve: {}".format(curve))
            self._private_key = ec.generate_private_key(
                _EC_CURVE_CLASSES[curve]())
        else:
            if int(key_bits) not in RSA_KEY_SIZES:
                raise ValueError("Unsupported RSA key size: {}".format(key_bits))
            self._private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=int(key_bits))
        self._key_type = key_type
        self._public_key = self._private_key.public_key()

    @property
    def key_type(self):
        """
        The key type (``"rsa"`` or ``"ec"``)

        :rtype: str
        """
        return self._key_type

    @property
    def private_key(self):
        """
        The private key

        :rtype: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
            cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey
        """
        return self._private_key

    @property
    def public_key(self):
        """
        The public key

        :rtype: cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey or
            cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKey
        """
        return self._public_key

    def private_key_as_pem(self, passphrase=None):
        """
        Return the private key as a PEM-encoded PKCS#8 structure.

        :param passphrase: If a `str` object is supplied, encrypt the private
            key with the passphrase before converting it to PEM format. If
            `None` is supplied, convert it to PEM format without performing any
            encryption.
        :return: private key in PEM format
        :rtype: bytes
        """
        if passphrase is None:
            encryption = serialization.NoEncryption()
        else:
            passphrase = passphrase if isinstance(passphrase, bytes) \
                else passphrase.encode()
            # PBES2 with AES-256-CBC and PBKDF2-HMAC-SHA256. The KDF
            # parameters are the ones the library picks; unlike for
            # PKCS#12, cryptography does not expose an encryption builder
            # for PKCS#8, so the iteration count is OpenSSL's default of
            # 2048 (the previous implementation used 25000).
            encryption = serialization.BestAvailableEncryption(passphrase)
        return self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption)


class _CertificateRequest(object):
    """
    Certificate request generator
    """
    def __init__(self, subject, key_pair, sans=None):
        """
        Constructor parameters:

        :param X509Name subject: subject to add to the certificate request
        :param _KeyPair key_pair: key pair whose private key signs the
            certificate request and whose public key it carries
        :param sans: collection of dns names to insert into a subjAltName
            extension for the certificate request
        :type sans: list(str) or tuple(str) or set(str)
        """
        builder = x509.CertificateSigningRequestBuilder().subject_name(
            self._subject_name(subject))
        builder = builder.add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=False)
        builder = builder.add_extension(
            x509.KeyUsage(digital_signature=True,
                          content_commitment=False,
                          key_encipherment=True,
                          data_encipherment=False,
                          key_agreement=False,
                          key_cert_sign=False,
                          crl_sign=False,
                          encipher_only=False,
                          decipher_only=False),
            critical=True)
        builder = builder.add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=False)
        if sans:
            builder = builder.add_extension(
                x509.SubjectAlternativeName(
                    [x509.DNSName(_bytes_to_unicode(san)) for san in sans]),
                critical=False)
        # An RSA key is signed with PKCS#1 v1.5 padding, an EC key with ECDSA;
        # both use SHA-256, as before.
        self._req = builder.sign(key_pair.private_key, _CRYPTO_SIGN_DIGEST)

    @staticmethod
    def _subject_name(subject):
        """
        Convert the supplied subject from a :class:`X509Name` into an X.509
        name

        :param X509Name subject: subject to convert
        :return: the X.509 name
        :rtype: cryptography.x509.Name
        """
        attributes = []
        for name, oid in _SUBJECT_ATTRIBUTES:
            value = getattr(subject, name)
            if value is not None:
                attributes.append(
                    x509.NameAttribute(oid, _bytes_to_unicode(value)))
        return x509.Name(attributes)

    def dump_to_pem(self):
        """
        Dump the certificate request to a PEM-encoded string

        :return: the certificate request PEM string
        :rtype: bytes
        """
        return self._req.public_bytes(serialization.Encoding.PEM)


class CsrAndPrivateKeyGenerator(object):
    """
    Certificate request and private key generator
    """
    def __init__(self, subject, sans=None, key_type=_CRYPTO_KEY_TYPE,
                 key_bits=_CRYPTO_KEY_BITS, curve=_CRYPTO_EC_CURVE):
        """
        Constructor parameters:

        :param X509Name subject: subject to add to the certificate request
        :param sans: collection of dns names to insert into a subjAltName
            extension for the certificate request
        :type sans: list(str) or tuple(str) or set(str)
        :param str key_type: ``"rsa"`` (default) or ``"ec"``
        :param int key_bits: RSA key size in bits (default 2048)
        :param str curve: named curve for EC keys (default secp256r1)
        """
        self._key_pair = _KeyPair(key_type, key_bits, curve)
        self._csr = _CertificateRequest(subject, self._key_pair, sans)

    def save_csr_and_private_key(self, csr_filename, private_key_filename,
                                 passphrase=None):
        """
        Save the certificate request and private key to disk in PEM format

        :param csr_filename: filename of the certificate request
        :param private_key_filename: filename of the private key
        :param passphrase: If a `str` object is supplied, encrypt the private
            key with the passphrase before converting it to PEM format. If
            `None` is supplied, convert it to PEM format without performing any
            encryption.
        """
        logger.info("Saving csr file to %s", csr_filename)
        DxlUtils.save_to_file(csr_filename, self._csr.dump_to_pem())
        logger.info("Saving private key file to %s", private_key_filename)
        DxlUtils.save_to_file(private_key_filename,
                              self._key_pair.private_key_as_pem(passphrase),
                              0o600)

    @property
    def csr(self):
        """
        Return the certificate request as PEM-encoded string

        :return: the PEM-encoded certificate request
        ​:rtype: str
        """
        return self._csr.dump_to_pem()


def validate_cert_pem(pem_text, message_on_exception=None):
    """
    Validate that the supplied `pem_text` string contains a PEM-encoded
    certificate

    :param str pem_text: text to validate as a PEM-encoded certificate
    :param str message_on_exception: extra text to add into an exception if
        a validation failure occurs
    :raise Exception: if the `pem_text` does not represent a valid PEM-encoded
        certificate
    """
    try:
        pem_bytes = pem_text if isinstance(pem_text, bytes) \
            else pem_text.encode()
        match = re.search(b"-----BEGIN ([A-Z0-9 ]+)-----", pem_bytes)
        if not match:
            raise Exception("No PEM data found")
        object_name = match.group(1).decode()
        if object_name != "CERTIFICATE":
            raise Exception(
                "Expected CERTIFICATE type for PEM, Received: {}".format(
                    object_name))
        x509.load_pem_x509_certificate(pem_bytes)
    except Exception as ex:
        logger.error("%s. Reason: %s",
                     message_on_exception or
                     "Failed to validate certificate PEM",
                     ex)
        logger.debug("Certificate PEM: %s", pem_text)
        raise
