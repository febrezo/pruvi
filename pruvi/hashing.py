import hashlib


def hash_bytes(data, hash_type="sha3_512"):
    """Hash a sequence of bytes

    Args:
        data (bytes): Set of hashes to hash.

    Returns:
        str. Hex digest.

    Raises:
        AttributeError.
    """
    m = getattr(hashlib, hash_type)()
    m.update(data)
    return m.hexdigest()
