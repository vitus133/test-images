#!/usr/bin/python3

import random
import zipfile
import subprocess
import os
import sys
import stat
import argparse
from jinja2 import Template


images = [
    {'size_mbytes': 150, 'qty': 25}
    ,{'size_mbytes': 250, 'qty': 25}
    ,{'size_mbytes': 300, 'qty': 10}
    ,{'size_mbytes': 400, 'qty': 4}
    ,{'size_mbytes': 500, 'qty': 4}
    ,{'size_mbytes': 600, 'qty': 5}
    ,{'size_mbytes': 800, 'qty': 2}
    ]

base_image_weight_mb = 60
port_range = (8000, 8004)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--registry',
        type=str, default="quay.io",
        help="Container registry to push images to (default - 'quay.io')")
    parser.add_argument('namespace',
        type=str,
        help="Registry namespace, for example `test_images'")
    parser.add_argument('-p', '--prefix',
        type=str, default="spam",
        help="Repository prefix (default - 'spam')")
    parser.add_argument('-t', '--tag',
        type=str, default="latest",
        help="Image tag (default - 'latest')")
    parser.add_argument('-U', '--username',
        type=str,
        help="Registry username")        
    parser.add_argument('-P', '--password',
        type=str,
        help="Registry password")        
    
    
    return parser.parse_args()

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
        sys.exit(1)


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
    tagged_to = f"{args.registry}/{args.namespace}/{fn}:{args.tag}"
    cmd = ["/usr/bin/podman",
           "build", ".",
           "--build-arg",
           f"ZIP_NAME={fn}",
           "-t",
           tagged_to,
           "-f",
           "Containerfile"]
    subprocess_wrapper(cmd)
    return tagged_to


def login():
    cmd = ["podman", "login",
           "-u", f"{args.username}",
           "-p", f"{args.password}",
           f"{args.registry}"]
    subprocess_wrapper(cmd)


def push_img(tagged_to: str):
    cmd = ["podman", "push",
           f"{tagged_to}"]
    subprocess_wrapper(cmd)


if __name__ == '__main__':
    args = get_args()
    try:
        report = []
        port = port_range[0]
        if args.username is not None and args.password is not None:
            login()
        for item in images:
            for instance in range(item.get('qty')):
                data = bytearray(random.getrandbits(8) for _ in range(
                    1048576 * (item.get(
                        'size_mbytes') - base_image_weight_mb)))
                fn = f"{args.prefix}_{item.get('size_mbytes')}_{instance}_{port}"

                with zipfile.ZipFile(fn, mode="a") as zf:
                    zf.writestr('1', bytes(data))

                print(f"written {fn}")
                render_entrypoint(port)
                port += 1
                if port > port_range[1]:
                    port = port_range[0]
                tagged_to = build_img(fn)
                os.unlink(fn)
                push_img(tagged_to)
                report.append(f"{args.registry}/{args.namespace}/{fn}:{args.tag}")
    except Exception as e:
        print(e)
        sys.exit(1)
    finally:
        with open("report.txt", "w") as rp:
            rp.write('\n'.join(report))
