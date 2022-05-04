#!/opt/homebrew/bin/python3

import shutil
import subprocess
import shlex
import sys
import ipaddress


class Error(Exception):
    pass


class PingScanError(Error):
    pass


def popen_send_ping(addr, count, timeout, stdout, stderr):
    cmd = []
    cmd.append(shutil.which("ping"))
    cmd.append(addr)
    cmd.append("-c {}".format(count))
    cmd.append("-t {}".format(timeout))

    args = shlex.split(' '.join(cmd))
    p = subprocess.Popen(args, stdout=stdout, stderr=stderr)
    return p


def decorate_exception(func):
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Error as e:
            print("============================================")
            print(e)
            print("============================================")
    return inner


def ping_scan(address):
    # Validation
    try:
        netlen = int(address.split('/')[1])
        if netlen < 24:
            raise PingScanError("Network length should be >= 24.")
        hosts = ipaddress.ip_network(address).hosts()
    except PingScanError as e:
        raise
    except Exception:
        raise PingScanError("Invalid Address:{}".format(address))

    procs = []
    null = open("/dev/null", "w")
    for ip in hosts:
        addr = str(ip)
        p = popen_send_ping(addr, 1, 1, null, null)
        procs.append((addr, p))

    line_format = "{:<15s} {:<10s}"
    print(line_format.format("address", "returncode"))
    for addr, p in procs:
        p.wait()
        if p.returncode == 0:
            print(line_format.format(addr, "OK"))


@decorate_exception
def main():
    if sys.version_info.major != 3:
        raise PingScanError("This python script is supported by python3")

    if len(sys.argv) != 2:
        raise PingScanError("Need Address.")

    ping_scan(sys.argv[1])


if __name__ == "__main__":
    main()
