# K12-Observatory
This project is around building a security scanner that scans for security vulnerabilities across all the public school districts in this country.
Implementation might include:

1) publicly discoverable first-party hostnames and IP addresses, based on certification transparency, passive DNS (FarSight), and domain enumeration
1) DNS records (including A and MX)
1) page contents
1) open ports and banner grabs
1) response times (ICMP and SYN) and up/down status to all hosts
1) automated vulnerability scans (maybe a simple Shodan query against the discovered IPs)
1) [CAIDA Telescope](https://www.caida.org/projects/network_telescope/) to see if any unsolicited scans originate from any of the K12 districts’ subnets (data request form [here](https://www.caida.org/catalog/datasets/telescope-near-real-time_dataset/))

This longitudinal dataset will hopefully allow us to answer a few questions:

1) Any changes in infrastructure, software upgrades, etc (malicious or not)
1) Defacements (e.g., compromised wordpress)
1) IoCs, including server load and server availability
1) Correlations between IoCs and disclosure
