import io
import unittest

from hypothesis import given
from hypothesis import strategies as st

from gmsad.keytab import Keyblock, KeytabEntry


class TestKeytabProperties(unittest.TestCase):

    @given(
        # Valid principal components (alphanumeric + basic symbols, 1 to 32 chars)
        components=st.lists(
            st.from_regex(r"^[a-zA-Z0-9_\-\.]{1,32}$", fullmatch=True),
            min_size=1,
            max_size=5
        ),
        # Valid Realm
        realm=st.from_regex(r"^[A-Z0-9_\-\.]{1,32}$", fullmatch=True),
        # kvno can be up to 32-bit unsigned integer
        kvno=st.integers(min_value=0, max_value=2**32 - 1),
        # timestamp up to 32-bit unsigned integer
        timestamp=st.integers(min_value=0, max_value=2**32 - 1),
        # key type (standard integer, e.g. 1 to 100)
        key_type=st.integers(min_value=1, max_value=100),
        # key bytes (arbitrary binary data)
        key_bytes=st.binary(min_size=1, max_size=64)
    )
    def test_keytab_entry_serialization_roundtrip(
        self, components, realm, kvno, timestamp, key_type, key_bytes
    ):
        princ = f"{'/'.join(components)}@{realm}"
        keyblock = Keyblock(key_type, key_bytes)
        entry = KeytabEntry(princ, kvno, timestamp, keyblock)

        # Write to memory stream
        stream = io.BytesIO()
        entry.to_stream(stream)

        # Reset stream to beginning
        stream.seek(0)

        # KeytabEntry.from_stream expects to read the entry starting from the size field.
        # So we can parse it back directly using from_stream
        read_entry, read_bytes = KeytabEntry.from_stream(stream)

        # Assert correct length of written stream
        self.assertEqual(len(stream.getvalue()), read_bytes)

        # Verify fields match original
        self.assertEqual(read_entry.principal, princ)
        self.assertEqual(read_entry.realm, realm)
        self.assertEqual(read_entry.components, components)
        self.assertEqual(read_entry.timestamp, timestamp)
        self.assertEqual(read_entry.vno, kvno)
        self.assertEqual(read_entry.key.type, key_type)
        self.assertEqual(read_entry.key.key, key_bytes)
