# test-images #

Creating test container images of different sizes to simulate customer' workload

There is a need for 100 unique images of different sizes:

Number of images          rough size 

25                   100-150 MB 

25                   200-250 MB 

10                   250-300 MB 

4                     400 MB 

4                     500 MB 

5                     600 MB 

2                     800 MB 

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
