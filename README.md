# test-images #

Creating test container images of different sizes to simulate customer' workload

There is a need for 100 unique images of different sizes:

| Number of images  | rough size    |
| ----------------- |:-------------:|
| 25                |  100-150 MB   |
| 25                |  200-250 MB   |
| 10                |  250-300 MB   |
| 4                 |  400 MB       |
| 4                 |  500 MB       |
| 5                 |  600 MB       |
| 2                 |  800 MB       |

The containers must be able to answer HTTP GET with 200 OK. There is a range of 5 TCP ports the container must bind to.

## Usage ##
```bash
usage: main.py [-h] [-r REGISTRY] [-p PREFIX] [-t TAG] [-U USERNAME]
               [-P PASSWORD]
               namespace

positional arguments:
  namespace             Registry namespace, for example `test_images'

optional arguments:
  -h, --help            show this help message and exit
  -r REGISTRY, --registry REGISTRY
                        Container registry to push images to (default -
                        'quay.io')
  -p PREFIX, --prefix PREFIX
                        Repository prefix (default - 'spam')
  -t TAG, --tag TAG     Image tag (default - 'latest')
  -U USERNAME, --username USERNAME
                        Registry username
  -P PASSWORD, --password PASSWORD1
                        Registry password
```
for example
```bash
python main.py test_images
```

The containers naming scheme:
`spam_<size>_<port>`
For example
`spam_150_0_8002` means that container size is about 150 mb and HTTP server binds to port 8002

## Test ## 
1. Run the container of the required size and port, for example:
  ```bash
  podman run -it --rm -p 8000:8000 quay.io/test_images/spam_250_5_8000:latest
  ```
2. In another terminal, send:
  ```bash
    $ curl -I -X GET  dhcp-55-222.lab.eng.tlv2.redhat.com:8000
  ```
  response:
  ```bash
    HTTP/1.0 200 OK
    Server: SimpleHTTP/0.6 Python/3.9.6
    Date: Tue, 03 Aug 2021 13:21:24 GMT
    Content-type: text/html; charset=utf-8
    Content-Length: 340

  ```
## Benchmarking the influence of logging ##
Test images can also create logs of the specified length with a specified frequency. To turn on the logging, two environment variables must be set in the pod specification, MESSAGE_LEN and LOG_PERIOD_SEC:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: log-injector
spec:
  containers:
  - image: quay.io/vgrinber/logging:latest
    imagePullPolicy: Always
    name: log-injector-container
    resources: {}
    env:
    - name: MESSAGE_LEN
      value: "100"
    - name: LOG_PERIOD_SEC
      value: "1/5"
    - name: POD_NAME
      valueFrom:
        fieldRef:
          fieldPath: metadata.name      

```
MESSAGE_LEN - number of random characters added to each log message after the pod name and the date
LOG_PERIOD_SEC - how much time (in seconds) we sleep before printing the next log message. It can be fractional as in the example (e.g. "1/8" or "0.125" should be fine)
The entrypoint must be set to log_injector.sh
Manual test:
```bash
$ podman run -it --entrypoint="/usr/src/srv/log_injector.sh" -e LOG_PERIOD_SEC=2 -e MESSAGE_LEN=20 -e POD_NAME=rrr quay.io/test_images/spam_50_0_8000:latest
rrr: Sat Apr 30 16:17:51 UTC 2022 MhloymjGkNDZ38ODv7rm
rrr: Sat Apr 30 16:17:53 UTC 2022 BLR8dcgkCjD8n0e1n9pt
rrr: Sat Apr 30 16:17:55 UTC 2022 yf0q1wVYFYs9jTsdRRaV
rrr: Sat Apr 30 16:17:57 UTC 2022 UKx7i9SP67ndH3AKcXTS
```
