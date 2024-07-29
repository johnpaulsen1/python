# Firewall Checker

The script `firewall_checker.py` can be used to check network connectivity between a source and destination host on a specific port.
It will also first proxy via default "nlup-unixmgt01" to ssh to the source host.

Below are the params the script accepts:
```
-p | --proxy        proxy (default is: nlup-unixmgt01)
-s | --source       source host (the source host that connection is tested from -> destination host)
-d | --destination  destination host (the source host will test connection on a specific port to the destination host)
-P | --port         port (the port that the source host will test connection to the destination host)
-t | --protocol     protocol type (protocol used to test the connection between source -> destination. Default is: tcp)
-u | --user         user (Kerberos user used to login to the proxy and the host)
-a | --authfile     auth file (full file path of file that contains the Kerberos username and password, in the format: <user>:<password>)
-q | --quiet        (setting this will run the script in 'quiet' mode, only showing the result of the connection attempt.)
-h | --help         (help menu will be desplayed)
```

## Example
```bash
$ ./firewall_checker.py -u <kerberos user> -s source_server1 -d destination_server1 -t tcp -P 20031

Enter Kerberos password for '<kerberos user>': 
Attempting to set proxy jump via: '<proxy server>'
Success!

Attempting to establish connection to source host: 'source_server1'.
Success!

Testing TCP connection from: 'source_server1' to: 'destination_server1' on port: '20031'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20031' Succeeded!
```

```bash
$ ./firewall_checker.py -a ~/.ssh/myauth -s source_server1 -d destination_server1 -t tcp -P 20031 -q

TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20031' Succeeded!
```

# Loop over connections
The script `mutiple_connections_checker.py` can be used to check network connectivity between multiple sources, multiple desinations, multiple protocols and multiple ports.
You need to feed the script a yaml file containing the network connections that needs to be tested.
The `mutiple_connections_checker.py` scripts calls the `firewall_checker.py` as needed.

## yaml file example
```yaml
---
monitoring:
  source:
    - source_server1
    - source_server2
    - source_server3
    - source_server4
  destination:
    - destination_server1
    - destination_server2
  protocols_ports:
    icmp: {}
    tcp:
      - 443
      - 22
      - 80
    udp:
      - 161
      - 623
backup1:
  source:
    - source_server1
  destination:
    - destination_server1
  protocols_ports:
    tcp:
      - 20031
      - 20100
      - 20200
      - 20300
      - 20400
      - 20500
      - 20600
      - 20700
      - 20800
      - 20900
    udp:
      - 20031
      - 20100
      - 20200
      - 20300
      - 20400
      - 20500
      - 20600
      - 20700
      - 20800
      - 20900
backup2:
  source:
    - source_server1
  destination:
    - destination_server1
  protocols_ports:
    tcp:
      - 20031
      - 20100
      - 20200
      - 20300
      - 20400
      - 20500
      - 20600
      - 20700
      - 20800
      - 20900
    udp:
      - 20031
      - 20100
      - 20200
      - 20300
      - 20400
      - 20500
      - 20600
      - 20700
      - 20800
      - 20900
backup3:
  source:
    - source_server1
  destination:
    - destination_server1
  protocols_ports:
    tcp:
      - 10011
      - 11000
      - 9443
```

## Loop over connections example:
```bash
$ ./mutiple_connections_checker.py -a ~/.ssh/mykauth -f ./test_connections.yaml

********************************************************************************
service: monitoring
testing ping from: 'source_server1' to: 'destination_server1'.
ICMP from: 'source_server1' to: 'destination_server1' Succeeded!
testing ping from: 'source_server1' to: 'destination_server2'.
ICMP from: 'source_server1' to: 'destination_server2' Succeeded!
testing ping from: 'source_server2' to: 'destination_server1'.
ICMP from: 'source_server2' to: 'destination_server1' Succeeded!
testing ping from: 'source_server2' to: 'destination_server2'.
ICMP from: 'source_server2' to: 'destination_server2' Succeeded!
testing ping from: 'source_server3' to: 'destination_server1'.
ICMP from: 'source_server3' to: 'destination_server1' Succeeded!
testing ping from: 'source_server3' to: 'destination_server2'.
ICMP from: 'source_server3' to: 'destination_server2' Succeeded!
testing ping from: 'source_server4' to: 'destination_server1'.
ICMP from: 'source_server4' to: 'destination_server1' Succeeded!
testing ping from: 'source_server4' to: 'destination_server2'.
ICMP from: 'source_server4' to: 'destination_server2' Succeeded!
--------------------------------------------------------------------------------
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '443'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '443' Succeeded!
testing: TCP connection from: 'source_server1' to: 'destination_server2' on port: '443'.
TCP Connection from: 'source_server1' to: 'destination_server2' on port: '443' Succeeded!
testing: TCP connection from: 'source_server2' to: 'destination_server1' on port: '443'.
TCP Connection from: 'source_server2' to: 'destination_server1' on port: '443' Succeeded!
testing: TCP connection from: 'source_server2' to: 'destination_server2' on port: '443'.
TCP Connection from: 'source_server2' to: 'destination_server2' on port: '443' Succeeded!
testing: TCP connection from: 'source_server3' to: 'destination_server1' on port: '443'.
TCP Connection from: 'source_server3' to: 'destination_server1' on port: '443' Succeeded!
testing: TCP connection from: 'source_server3' to: 'destination_server2' on port: '443'.
TCP Connection from: 'source_server3' to: 'destination_server2' on port: '443' Succeeded!
testing: TCP connection from: 'source_server4' to: 'destination_server1' on port: '443'.
TCP Connection from: 'source_server4' to: 'destination_server1' on port: '443' Succeeded!
testing: TCP connection from: 'source_server4' to: 'destination_server2' on port: '443'.
TCP Connection from: 'source_server4' to: 'destination_server2' on port: '443' Succeeded!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '22'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '22' Succeeded!
testing: TCP connection from: 'source_server1' to: 'destination_server2' on port: '22'.
TCP Connection from: 'source_server1' to: 'destination_server2' on port: '22' Succeeded!
testing: TCP connection from: 'source_server2' to: 'destination_server1' on port: '22'.
TCP Connection from: 'source_server2' to: 'destination_server1' on port: '22' Succeeded!
testing: TCP connection from: 'source_server2' to: 'destination_server2' on port: '22'.
TCP Connection from: 'source_server2' to: 'destination_server2' on port: '22' Succeeded!
testing: TCP connection from: 'source_server3' to: 'destination_server1' on port: '22'.
TCP Connection from: 'source_server3' to: 'destination_server1' on port: '22' Succeeded!
testing: TCP connection from: 'source_server3' to: 'destination_server2' on port: '22'.
TCP Connection from: 'source_server3' to: 'destination_server2' on port: '22' Succeeded!
testing: TCP connection from: 'source_server4' to: 'destination_server1' on port: '22'.
TCP Connection from: 'source_server4' to: 'destination_server1' on port: '22' Succeeded!
testing: TCP connection from: 'source_server4' to: 'destination_server2' on port: '22'.
TCP Connection from: 'source_server4' to: 'destination_server2' on port: '22' Succeeded!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '80'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '80' Succeeded!
testing: TCP connection from: 'source_server1' to: 'destination_server2' on port: '80'.
TCP Connection from: 'source_server1' to: 'destination_server2' on port: '80' Succeeded!
testing: TCP connection from: 'source_server2' to: 'destination_server1' on port: '80'.
TCP Connection from: 'source_server2' to: 'destination_server1' on port: '80' Succeeded!
testing: TCP connection from: 'source_server2' to: 'destination_server2' on port: '80'.
TCP Connection from: 'source_server2' to: 'destination_server2' on port: '80' Succeeded!
testing: TCP connection from: 'source_server3' to: 'destination_server1' on port: '80'.
TCP Connection from: 'source_server3' to: 'destination_server1' on port: '80' Succeeded!
testing: TCP connection from: 'source_server3' to: 'destination_server2' on port: '80'.
TCP Connection from: 'source_server3' to: 'destination_server2' on port: '80' Succeeded!
testing: TCP connection from: 'source_server4' to: 'destination_server1' on port: '80'.
TCP Connection from: 'source_server4' to: 'destination_server1' on port: '80' Succeeded!
testing: TCP connection from: 'source_server4' to: 'destination_server2' on port: '80'.
TCP Connection from: 'source_server4' to: 'destination_server2' on port: '80' Succeeded!
--------------------------------------------------------------------------------
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '161'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '161' Succeeded!
testing: UDP connection from: 'source_server1' to: 'destination_server2' on port: '161'.
UDP Connection from: 'source_server1' to: 'destination_server2' on port: '161' Succeeded!
testing: UDP connection from: 'source_server2' to: 'destination_server1' on port: '161'.
UDP Connection from: 'source_server2' to: 'destination_server1' on port: '161' Succeeded!
testing: UDP connection from: 'source_server2' to: 'destination_server2' on port: '161'.
UDP Connection from: 'source_server2' to: 'destination_server2' on port: '161' Succeeded!
testing: UDP connection from: 'source_server3' to: 'destination_server1' on port: '161'.
UDP Connection from: 'source_server3' to: 'destination_server1' on port: '161' Succeeded!
testing: UDP connection from: 'source_server3' to: 'destination_server2' on port: '161'.
UDP Connection from: 'source_server3' to: 'destination_server2' on port: '161' Succeeded!
testing: UDP connection from: 'source_server4' to: 'destination_server1' on port: '161'.
UDP Connection from: 'source_server4' to: 'destination_server1' on port: '161' Succeeded!
testing: UDP connection from: 'source_server4' to: 'destination_server2' on port: '161'.
UDP Connection from: 'source_server4' to: 'destination_server2' on port: '161' Succeeded!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '623'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '623' Succeeded!
testing: UDP connection from: 'source_server1' to: 'destination_server2' on port: '623'.
UDP Connection from: 'source_server1' to: 'destination_server2' on port: '623' Succeeded!
testing: UDP connection from: 'source_server2' to: 'destination_server1' on port: '623'.
UDP Connection from: 'source_server2' to: 'destination_server1' on port: '623' Succeeded!
testing: UDP connection from: 'source_server2' to: 'destination_server2' on port: '623'.
UDP Connection from: 'source_server2' to: 'destination_server2' on port: '623' Succeeded!
testing: UDP connection from: 'source_server3' to: 'destination_server1' on port: '623'.
UDP Connection from: 'source_server3' to: 'destination_server1' on port: '623' Succeeded!
testing: UDP connection from: 'source_server3' to: 'destination_server2' on port: '623'.
UDP Connection from: 'source_server3' to: 'destination_server2' on port: '623' Succeeded!
testing: UDP connection from: 'source_server4' to: 'destination_server1' on port: '623'.
UDP Connection from: 'source_server4' to: 'destination_server1' on port: '623' Succeeded!
testing: UDP connection from: 'source_server4' to: 'destination_server2' on port: '623'.
UDP Connection from: 'source_server4' to: 'destination_server2' on port: '623' Succeeded!
--------------------------------------------------------------------------------

********************************************************************************
service: backup1
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20031'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20031' Succeeded!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20100'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20100' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20200'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20200' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20300'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20300' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20400'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20400' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20500'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20500' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20600'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20600' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20700'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20700' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20800'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20800' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20900'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20900' Failed!
--------------------------------------------------------------------------------
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20031'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20031' Succeeded!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20100'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20100' Succeeded!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20200'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20200' Succeeded!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20300'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20300' Succeeded!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20400'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20400' Succeeded!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20500'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20500' Succeeded!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20600'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20600' Succeeded!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20700'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20700' Succeeded!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20800'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20800' Succeeded!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20900'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20900' Succeeded!
--------------------------------------------------------------------------------

********************************************************************************
service: backup2
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20031'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20031' Succeeded!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20100'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20100' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20200'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20200' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20300'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20300' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20400'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20400' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20500'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20500' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20600'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20600' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20700'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20700' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20800'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20800' Failed!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '20900'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '20900' Failed!
--------------------------------------------------------------------------------
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20031'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20031' Succeeded!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20100'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20100' Failed!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20200'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20200' Failed!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20300'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20300' Failed!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20400'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20400' Failed!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20500'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20500' Failed!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20600'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20600' Failed!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20700'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20700' Failed!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20800'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20800' Failed!
testing: UDP connection from: 'source_server1' to: 'destination_server1' on port: '20900'.
UDP Connection from: 'source_server1' to: 'destination_server1' on port: '20900' Failed!
--------------------------------------------------------------------------------

********************************************************************************
service: backup3
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '10011'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '10011' Succeeded!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '11000'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '11000' Succeeded!
testing: TCP connection from: 'source_server1' to: 'destination_server1' on port: '9443'.
TCP Connection from: 'source_server1' to: 'destination_server1' on port: '9443' Succeeded!
--------------------------------------------------------------------------------
```
