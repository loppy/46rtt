#!/usr/bin/env python

#
# usage:
# $ python3.5 46rtt.py <alexa top list> <the number of target>
#

import sys
import subprocess
import ipaddress
import re


# check dns look up results
def return_ip_addr(dig_results):
    for ip_addr in dig_results:
        try:
            ipaddress.ip_address(ip_addr)
            return ip_addr
        except:
            continue

    return False


# get ipv6 address
def ipv6_lookup(domain):
    cmd = ["dig"]
    cmd.append("www." + domain)
    cmd.append("AAAA")
    cmd.append("+short")

    tmp = subprocess.check_output(cmd, universal_newlines=True)
    ipv6_addr = return_ip_addr(tmp.split("\n"))

    if ipv6_addr:
        return ipv6_addr
    else:
        return False


# get ipv4 address
def ipv4_lookup(domain):
    cmd = ["dig"]
    cmd.append("www." + domain)
    cmd.append("A")
    cmd.append("+short")

    tmp = subprocess.check_output(cmd, universal_newlines=True)
    ipv4_addr = return_ip_addr(tmp.split("\n"))

    if ipv4_addr:
        return ipv4_addr
    else:
        return False


# send an ipv4 ping and return the rtt
def v4_ping(ipv4_addr):
    ping_command = ["ping", "-c", "1", ipv4_addr]

    try:
        ping_output = subprocess.check_output(
            ping_command, universal_newlines=True)
        m = re.search(r'time=\d+\.\d+', ping_output)
        (time, rttstr) = m.group(0).split('=')
        print(rttstr)
        return rttstr
    except subprocess.CalledProcessError:
        return False


# send an ipv6 ping and return the rtt
def v6_ping(ipv6_addr):
    ping_command = ["ping6", "-c", "1", ipv6_addr]

    try:
        ping_output = subprocess.check_output(
            ping_command, universal_newlines=True)
        m = re.search(r'time=\d+\.\d+', ping_output)
        (time, rttstr) = m.group(0).split('=')
        print(rttstr)
        return rttstr
    except subprocess.CalledProcessError:
        return False

# url list for the lookup
url_list = []
results = {}

# you must specify s
url_list_file_name = sys.argv[1]
url_list_file = open(url_list_file_name, 'r')

# the number of target from top 1 to N
target_num = int(sys.argv[2])

# separate id and domain
for line in url_list_file:
    url_list.append(line[:-1].split(",")[1])

for domain in url_list[0:target_num]:
    ipv4_addr = ipv4_lookup(domain)
    ipv6_addr = ipv6_lookup(domain)

    # if the domain has both ipv4 and ipv6 address
    if ipv6_addr and ipv4_addr:
        print(domain)
        results[domain] = {}
        results[domain]["4"] = []
        results[domain]["6"] = []
        results[domain]["4"].append(float(v4_ping(ipv4_addr)))
        results[domain]["6"].append(float(v6_ping(ipv6_addr)))

# output the results as a csv file
# csv format: 
#   <domain>,<v4 rtt (msec)>, <v6 rtt (msec)>
output_file = open("result.csv", "a")
for domain in results.keys():
    output_line = domain + "," + \
        str(results[domain]["4"][0]) + "," + \
        str(results[domain]["6"][0]) + "\n"
    output_file.write(output_line)

output_file.close()
