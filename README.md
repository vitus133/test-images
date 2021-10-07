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
python main.py <registry fqdn>
```
for example
```bash
python main.py dhcp-55-222.lab.eng.tlv2.redhat.com:5000
```

The containers naming scheme:
`spam_<size>_<port>`
For example
`spam_150_8002` means that container size is about 150 mb and HTTP server binds to port 8002

The registry assumes username `dummy` and password `dummy` in this version

## Test ## 
1. Run the container of the required size and port, for example:
  ```bash
  podman run -it --rm -p 8000:8000 dhcp-55-222.lab.eng.tlv2.redhat.com:5000/spam_250_5_8000:latest
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

When deployed, it will produce logs like that:
```bash
oc logs pod/log-injector -f
log-injector: Wed Oct  6 20:09:35 UTC 2021 LsmA6K8jN3mg5weQf0uZpZEn127Bqb0hYQ0tMPto0E4f7lYKELEvcg8py6UYWGDOxYq5rmkC7Y4Z5yQtJp8h0IiGlumcHVW8UJ3A
log-injector: Wed Oct  6 20:09:35 UTC 2021 sSp4P7e3rqxgTieD2OACCFCvgmVmS0yzFJMsgg0DTcwQrEee1dAtMUd9ss8DkFslvLtlISTgUQ6GdquL2npz7c4DzqSe7TYMd8ah
log-injector: Wed Oct  6 20:09:35 UTC 2021 LdAteyqrR5XBXbwrKxYiiPMAmlin8dHShCtZLJaP5DqU8Kaotg3s8spVmnpt5vEQOBfSkZ40ygFKHHbRQVY2Z622AgEMGcMW0ule
log-injector: Wed Oct  6 20:09:35 UTC 2021 oNv572cMqfyHLmQjOuv6h2GiwidzFHPHKM4JfX3f06ifgvroULT6ruKeqQdz3WZgj8ZqyfxWglmFSLhc0cP9x5v2jh74Eka4Tzct
log-injector: Wed Oct  6 20:09:36 UTC 2021 Wol1kllESDPXUcNfsfqVoLKbGmUd1buaEDEePkxGBr4lQPjzIQpROaPZZkiCjScC2VRUl7BLJ4ghkT4Y0qEC0tnUMyuY23YkL1Yd
log-injector: Wed Oct  6 20:09:36 UTC 2021 9AwM7x83WyDlBgBPotqesfH4iv1v5BI68asqrVSkrsedcea9e26qh1msiV7aBnGHFStcnYSo4G6wAYBOGXvaANXsdJYAH3E4d6g3
log-injector: Wed Oct  6 20:09:36 UTC 2021 oPz8bjYAPsPuc1VgzGdms2mFkJBDL6aZOpyhxn7C6ASySY6zHono9BWdEaa922nSiAMPoX4b2cqkc8NdcyqaEWeThieT34sj92CV
log-injector: Wed Oct  6 20:09:36 UTC 2021 2sDshIALy9wcRfdDaWJozv7wlX7EUZzQ0fkSMBoaH122w2he1QGcWXUYB1HiWAnaWy4R7eAhWod0sjKN0rxWNQf8vS0C4ohAOypq
log-injector: Wed Oct  6 20:09:36 UTC 2021 Nk8UcsXr5Hg0agha8LUF8n5X67zkmxbw8CGpUZZEi3nnWqbwhjgCIQ3lOfDQbW6iQNSIs346KIf0Bw9gNi4MU1fHabxLtXM8kUnv
```
