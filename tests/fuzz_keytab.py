import io
import logging
import struct
import sys
from pathlib import Path

try:
    import atheris
except ImportError:
    atheris = None

if atheris is not None:
    with atheris.instrument_imports():
        from gmsad.keytab import (
            EmptyKeytabEntry,
            EndOfKeytabEntries,
            InvalidPrincipal,
            Keytab,
        )
else:
    from gmsad.keytab import (
        EmptyKeytabEntry,
        EndOfKeytabEntries,
        InvalidPrincipal,
        Keytab,
    )


def TestOneInput(data):
    fd = io.BytesIO(data)

    # Try reading the full keytab stream
    try:
        kt = Keytab()
        kt.read(fd)
    except (
        EndOfKeytabEntries,
        EmptyKeytabEntry,
        InvalidPrincipal,
        UnicodeDecodeError,
        AssertionError,
        struct.error,
        IndexError,
    ):
        # These are expected exceptions when parsing invalid/corrupted inputs.
        pass
    except Exception as e:
        # Any other unhandled exception is a potential bug.
        raise e


def bootstrap_seed_corpus(dirs):
    if not dirs:
        return
    corpus_dir = Path(dirs[0])
    if corpus_dir.exists() and not any(corpus_dir.iterdir()):
        # Generate a small valid keytab and write it as seed
        kt = Keytab()
        kt.add_entry("test/user@REALM", "salt", 1, b"secretpassword", 0x18)
        kt.write(str(corpus_dir / "seed1.keytab"))
        print(f"Bootstrapped empty corpus directory '{corpus_dir}' with a valid seed keytab.")


def main():
    if atheris is None:
        print("Atheris is not installed. Fuzzing is only supported on environments where Atheris is available (e.g. Linux).")
        sys.exit(0)

    logging.disable(logging.CRITICAL)

    # Filter out atheris flags (start with -) to extract corpus dirs
    corpus_dirs = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    bootstrap_seed_corpus(corpus_dirs)

    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
