"""SRI (Subresource Integrity) verification using SHA-256/384/512."""

from __future__ import annotations

import base64
import hashlib

from anml_client.errors import SriVerificationError

_SUPPORTED_ALGORITHMS = {"sha256", "sha384", "sha512"}


def _get_hash_func(algorithm: str) -> str:
    """Map SRI algorithm name to hashlib name."""
    mapping = {
        "sha256": "sha256",
        "sha384": "sha384",
        "sha512": "sha512",
    }
    alg = algorithm.lower().replace("-", "")
    if alg not in mapping:
        raise SriVerificationError(f"Unsupported algorithm: {algorithm}")
    return mapping[alg]


def compute_sri(data: bytes, algorithm: str = "sha256") -> str:
    """Compute an SRI hash for the given data.

    Args:
        data: The data to hash.
        algorithm: The hash algorithm (sha256, sha384, or sha512).

    Returns:
        SRI string in format "algorithm-base64hash".

    Raises:
        SriVerificationError: If the algorithm is unsupported.
    """
    hash_name = _get_hash_func(algorithm)
    digest = hashlib.new(hash_name, data).digest()
    b64 = base64.b64encode(digest).decode("ascii")
    return f"{algorithm}-{b64}"


def verify_sri(data: bytes, expected: str) -> bool:
    """Verify data against an SRI hash string.

    Args:
        data: The data to verify.
        expected: The expected SRI string (e.g., "sha256-base64hash").

    Returns:
        True if verification passes, False otherwise.

    Raises:
        SriVerificationError: If the SRI string format is invalid.
    """
    if not expected or "-" not in expected:
        raise SriVerificationError(f"Invalid SRI format: {expected}")

    parts = expected.split("-", 1)
    if len(parts) != 2:
        raise SriVerificationError(f"Invalid SRI format: {expected}")

    algorithm, expected_hash = parts

    if algorithm.lower() not in _SUPPORTED_ALGORITHMS:
        raise SriVerificationError(f"Unsupported algorithm: {algorithm}")

    computed = compute_sri(data, algorithm)
    return computed == expected
