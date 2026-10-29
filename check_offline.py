#!/usr/bin/env python3
"""Confirm a surrounding network-denial sandbox, then run the finite controls."""
import errno
import socket
import subprocess
import sys
from pathlib import Path

if __name__ == '__main__':
    # AF_INET socket creation is denied by macOS Seatbelt network* policy.
    # Loopback only: this control never contacts an external host.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.settimeout(0.5)
            probe.connect(('127.0.0.1', 9))
    except OSError as exc:
        if exc.errno not in (errno.EPERM, errno.EACCES):
            raise SystemExit(f'Network denial not established: {exc}')
        print(f'PASS network operation denied (errno={exc.errno})', flush=True)
    else:
        raise SystemExit('Network operation was allowed; refusing offline claim')
    subprocess.run([sys.executable, str(Path(__file__).with_name('reproduce.py'))], check=True)
