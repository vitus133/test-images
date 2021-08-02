#!/usr/bin/python3

import random
import zipfile
import subprocess
import os
import sys

images = [
    {'size_mbytes': 150, 'qty': 25},
    {'size_mbytes': 250, 'qty': 25},
    {'size_mbytes': 300, 'qty': 10},
    {'size_mbytes': 400, 'qty': 4},
    {'size_mbytes': 500, 'qty': 4},
    {'size_mbytes': 600, 'qty': 5},
    {'size_mbytes': 800, 'qty': 2}]

base_image_weight_mb = 55


def build_img(fn: str):
    cmd = ["/usr/bin/podman",
           "build",
           "--build-arg",
           f"ZIP_NAME={fn}",
           "-t",
           f"{fn}:latest",
           "-f",
           "Containerfile"]
    cwd = os.getcwd()
    try:
        with subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd) as pm:
            output = pm.communicate()
            print(output[0].decode())
            if len(output[1]):
                raise Exception(
                    f"Container build failed: {output[1].decode()}")
    except exception as cpe:
        print(cpe)
        exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py 'target_registry'")
        exit(1)
    for item in images:
        for instance in range(item.get('qty')):
            data = bytearray(random.getrandbits(8) for _ in range(
                1048576 * (item.get(
                    'size_mbytes') - base_image_weight_mb)))
            fn = f"spam_{item.get('size_mbytes')}_{instance}"

            with zipfile.ZipFile(fn, mode="a") as zf:
                zf.writestr('1', bytes(data))

            print(f"written {fn}")
            build_img(fn)
            os.unlink(fn)
            exit(0)
