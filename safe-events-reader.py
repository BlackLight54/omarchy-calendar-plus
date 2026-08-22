#!/usr/bin/env python3
"""Read a small regular file without following links or blocking on FIFOs."""

import os
import stat
import sys


MAX_BYTES = 65_536


def main() -> int:
    if len(sys.argv) != 2:
        return 2

    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK
    flags |= os.O_NOFOLLOW

    try:
        descriptor = os.open(sys.argv[1], flags)
    except OSError:
        return 2

    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_BYTES:
            return 2

        chunks = []
        total = 0
        while total <= MAX_BYTES:
            chunk = os.read(descriptor, min(8192, MAX_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)

        if total > MAX_BYTES:
            return 2
        sys.stdout.buffer.write(b"".join(chunks))
        return 0
    except OSError:
        return 2
    finally:
        os.close(descriptor)


if __name__ == "__main__":
    raise SystemExit(main())
