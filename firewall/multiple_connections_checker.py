#!/usr/bin/env python

import argparse, os, yaml
from termcolor import colored

# Parse arguments
'''
    -a    authfile (file that contains the Kerberos password for the user)
    -f    file (yaml file that contains the network connections to test)
    -p    proxy (default is: nlup-unixmgt01)
'''

parser = argparse.ArgumentParser(description="Python script that loops over a yaml file containing the source -> destination connections to be tested, it makes a call to: ./firewall_checker.py to perform the check.")
parser.add_argument('-a', '--authfile', help="Location of the authfile containing credentials of the Kerberos user.", required=True, dest='authfile')
parser.add_argument('-f', '--file', help='The filepath of the yaml file containing the connections to test.', required=True, dest='file')
parser.add_argument('-p', '--proxy', help='The proxy jump host used to connect to the source host.', required=False, default='nlup-unixmgt01', dest='proxy')
args = parser.parse_args()


try:
    conn_file = open(args.file)
except Exception as e:
    error = "Unable to open file: '{}'.".format(args.file)
    print(colored(error, 'red'))
    print(colored('Exception:', 'red'))
    print(colored(str(e), 'red'))
    exit(1)

try:
    service_connections = yaml.load(conn_file, Loader=yaml.FullLoader)
except Exception as e:
    error = "Failed to read yaml contents of file: '{}'\nEnsure that the file is in yaml format, refer to ./README.md.".format(args.file)
    print(colored(error, 'red'))
    print(colored('Exception:', 'red'))
    print(colored(str(e), 'red'))
    exit(1)

try:
    conn_file.close()
except Exception as e:
    error = "Failed to close file: '{}'.".format(args.file)
    print(colored(error, 'red'))
    print(colored('Exception:', 'red'))
    print(colored(str(e), 'red'))

try:
    for service in service_connections:
        print('*'*80)
        print('service: {}'.format(service))
        try:
            for k, v in service_connections[service].items():
                if k == 'source':
                    source_array = v
                if k == 'destination':
                    destination_array = v
                if k == 'protocols_ports':
                    protocols_ports = v
        except KeyboardInterrupt as ki:
            error = 'User initiated a Keyboard Interrupt... Quiting....'
            print(error)
            exit(1)

        try:
            for protocol, ports in protocols_ports.items():
                if protocol == 'icmp':
                    for source in source_array:
                        for destination in destination_array:
                            print("testing ping from: '{}' to: '{}'.".format(source, destination))
                            try:
                                os.system('./firewall_checker.py -a {} -P {} -s {} -d {} -t {} -q'.format(args.authfile, args.proxy, source, destination, protocol))
                            except KeyboardInterrupt as ki:
                                error = 'User initiated a Keyboard Interrupt... Quiting....'
                                print(error)
                                exit(1)
                            except Exception as e:
                                error = "Script: '{}' failed.".format(__file__)
                                print(colored(error, 'red'))
                                print(colored('Exception:', 'red'))
                                print(colored(str(e), 'red'))
                                exit(2)
                else:
                    for port in ports:
                        for source in source_array:
                            for destination in destination_array:
                                print("testing: {} connection from: '{}' to: '{}' on port: '{}'.".format(protocol.upper(), source, destination, port))
                                try:
                                    os.system('./firewall_checker.py -a {} -P {} -s {} -d {} -t {} -p {} -q'.format(args.authfile, args.proxy, source, destination, protocol, port))
                                except KeyboardInterrupt as ki:
                                    error = 'User initiated a Keyboard Interrupt... Quiting....'
                                    print(error)
                                    exit(1)
                                except Exception as e:
                                    error = "Script: '{}' failed.".format(__file__)
                                    print(colored(error, 'red'))
                                    print(colored('Exception:', 'red'))
                                    print(colored(str(e), 'red'))
                                    exit(2)
                print('-'*80)
        except KeyboardInterrupt as ki:
            error = 'User initiated a Keyboard Interrupt... Quiting....'
            print(error)
            exit(1)
        print()
except KeyboardInterrupt as ki:
    error = 'User initiated a Keyboard Interrupt... Quiting....'
    print(error)
    exit(1)
