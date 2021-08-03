#!/usr/bin/python3

import random
import zipfile
import subprocess
import os
import sys
import stat
from jinja2 import Template


images = [
    {'size_mbytes': 150, 'qty': 25},
    {'size_mbytes': 250, 'qty': 25},
    {'size_mbytes': 300, 'qty': 10},
    {'size_mbytes': 400, 'qty': 4},
    {'size_mbytes': 500, 'qty': 4},
    {'size_mbytes': 600, 'qty': 5},
    {'size_mbytes': 800, 'qty': 2}]

base_image_weight_mb = 60
port_range = (8000, 8004)


def subprocess_wrapper(cmd: list):
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
                print(f"stderr: {output[1].decode()}")
    except Exception as cpe:
        print(cpe)
        exit(1)


def render_entrypoint(port: int):
    script_name = "server.sh"
    with open("templates/server.sh.j2", "r") as tf:
        tm = Template(tf.read())
    with open(script_name, "w") as sf:
        sf.write(tm.render(port=port))
    st = os.stat(script_name)
    os.chmod(
        script_name, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    

def build_img(fn: str):
    cmd = ["/usr/bin/podman",
           "build",
           "--build-arg",
           f"ZIP_NAME={fn}",
           "-t",
           f"{fn}:latest",
           "-f",
           "Containerfile"]
    subprocess_wrapper(cmd)


def login(username: str, password: str, registry: str):
    cmd = ["podman", "login",
           "-u", f"{username}",
           "-p", f"{password}",
           f"{registry}"]
    subprocess_wrapper(cmd)


def push_img(registry:str, imgname:str):
    cmd = ["podman", "push",
           f"{imgname}:latest",
           f"{registry}/{imgname}:latest"]
    subprocess_wrapper(cmd)


if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print("Usage: python main.py 'target_registry'")
            exit(1)
        report = []
        port = port_range[0]
        login("dummy", "dummy", sys.argv[1])
        for item in images:
            for instance in range(item.get('qty')):
                data = bytearray(random.getrandbits(8) for _ in range(
                    1048576 * (item.get(
                        'size_mbytes') - base_image_weight_mb)))
                fn = f"spam_{item.get('size_mbytes')}_{instance}_{port}"

                with zipfile.ZipFile(fn, mode="a") as zf:
                    zf.writestr('1', bytes(data))

                print(f"written {fn}")
                render_entrypoint(port)
                port += 1
                if port > port_range[1]:
                    port = port_range[0]
                build_img(fn)
                os.unlink(fn)
                push_img(sys.argv[1], fn)
                report.append(f"{sys.argv[1]}/{fn}:latest")
    except Exception as e:
        print(e)
        exit(1)
    finally:
        with open("report.txt", "w") as rp:
            rp.write('\n'.join(report))
