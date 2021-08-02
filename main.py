#!/usr/bin/python3

import random
import zipfile

images = [
    {'size_mbytes': 100, 'qty': 25},
    {'size_mbytes': 200, 'qty': 25},
    {'size_mbytes': 250, 'qty': 10},
    {'size_mbytes': 400, 'qty': 4},
    {'size_mbytes': 500, 'qty': 4},
    {'size_mbytes': 600, 'qty': 5},
    {'size_mbytes': 800, 'qty': 2}]


def build_img(fn: str):
    pass

if __name__ == '__main__':
    for item in images:
        for instance in range(item.get('qty')):
            data = bytearray(random.getrandbits(8) for _ in range(
                1048576 * item.get('size_mbytes')))  # One MB * size
            fn = f"spam_{item.get('size_mbytes')}_{instance}"
            with zipfile.ZipFile(fn, mode="a") as zf:
                zf.writestr('1', bytes(data), compress_type=zipfile.ZIP_DEFLATED)
                print(f"written {fn}")
