import io
import logging
import struct
import sys
from pathlib import Path

from gmsad.keytab import (
    EmptyKeytabEntry,
    EndOfKeytabEntries,
    InvalidPrincipal,
    Keytab,
)


def run_file(filepath: Path):
    with filepath.open("rb") as f:
        data = f.read()

    fd = io.BytesIO(data)
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
        pass


def main():
    logging.disable(logging.CRITICAL)

    if len(sys.argv) < 2:
        print("Usage: python -m tests.run_corpus <corpus_directory_path>")
        sys.exit(1)

    corpus_dir = Path(sys.argv[1])
    if not corpus_dir.is_dir():
        print(f"Error: {corpus_dir} is not a directory.")
        sys.exit(1)

    files = [f for f in corpus_dir.iterdir() if f.is_file()]
    print(f"Running {len(files)} files from corpus directory: {corpus_dir}")

    for f in files:
        run_file(f)

    print("Done executing corpus files.")


if __name__ == "__main__":
    main()
