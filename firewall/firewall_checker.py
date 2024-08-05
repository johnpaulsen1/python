#!/usr/bin/env python

import argparse, getpass, os, paramiko
from termcolor import colored, cprint

def getSSHConnection(proxyHost, hostName, user, password, quiet):
    # setup SSH connection
    try:
        sshconf = paramiko.SSHConfig()
        sshconf.parse(open((os.path.expanduser('~/.ssh/config'))))
    except KeyboardInterrupt as ki:
        error = 'User initiated a Keyboard Interrupt... Quiting....'
        print(error)
        exit(1)
    except Exception as e:
        error = 'Unable to set ssh config.'
        print(colored(error, 'yellow'))
        print(colored('Exception:', 'yellow'))
        print(colored(str(e), 'yellow'))
        print(colored('Attempting to proceed without the ssh config set.', 'yellow'))

    if proxyHost != hostName:
        if not quiet:
            userMessage = "Attempting to set proxy jump via: '{}'".format(proxyHost)
            print(userMessage)

        # set proxy jump connection
        try:
            proxy_client = paramiko.SSHClient()
            proxy_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            proxy_client.connect(proxyHost, 22, username=user, password=password, look_for_keys=False)
            transport = proxy_client.get_transport()
            destination_conn = (hostName, 22)
            local_conn = ('127.0.0.1', 22)
            proxy_channel = transport.open_channel("direct-tcpip", destination_conn, local_conn)

            if not quiet:
                userMessage = "Success!"
                print(colored(userMessage, 'green'))
                print()
        except KeyboardInterrupt as ki:
            error = 'User initiated a Keyboard Interrupt... Quiting....'
            print(error)
            exit(1)
        except Exception as e:
            error = "Unable to set proxy connection via: '{}'.".format(proxyHost)
            print(colored(error, 'yellow'))
            print(colored('Exception:', 'yellow'))
            print(colored(str(e), 'yellow'))
            print(colored('Attempting to proceed without the proxy set.', 'yellow'))
            proxy_channel = None
    else:
        proxy_channel = None
    
    if not quiet:
        userMessage = "Attempting to establish connection to source host: '{}'.".format(hostName)
        print(userMessage)

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostName, 22, username=user, password=password,
                       sock=proxy_channel, timeout=10, auth_timeout=5,
                       allow_agent=False, look_for_keys=False,
                       banner_timeout=100)
        if not quiet:
            userMessage = "Success!"
            print(colored(userMessage, 'green'))
            print()
        return client
    except KeyboardInterrupt as ki:
        error = 'User initiated a Keyboard Interrupt... Quiting....'
        print(error)
        exit(1)
    except paramiko.ssh_exception.SSHException as e:
        error = "A ssh exception was caught while connecting to: '{}', via proxy: '{}'.".format(hostName, proxyHost)
        print(colored(error, 'red'))
        print(colored('Exception:', 'red'))
        print(colored(str(e), 'red'))
        client = None
        return client
    except paramiko.ssh_exception.AuthenticationException as e:
        error = "Unable to establish connection to: '{}'.".format(hostName)
        print(colored(error, 'red'))
        print(colored('Exception:', 'red'))
        print(colored(str(e), 'red'))
        if 'timed out' in str(e):
            error = 'Check your internet / vpn connection.'
            print(colored(error, 'red'))
            exit(1)
        client = None
        return client
    except Exception as e:
        error = "Unable to establish connection to: '{}'.".format(hostName)
        print(colored(error, 'red'))
        print(colored('Exception:', 'red'))
        print(colored(str(e), 'red'))
        if 'timed out' in str(e):
            error = 'Check your internet / vpn connection.'
            print(colored(error, 'red'))
            exit(1)
        client = None
        return client


def runCmdOnClient(ssh_client, command):
    cmdOutputList = list()
    cmdAttrs = list()
    try:
        transport = ssh_client.get_transport()
        ssh_session = transport.open_session()
        ssh_session.set_combine_stderr(True)
        ssh_session.exec_command(command)
        stdout = ssh_session.makefile('rb', -1)
        try:
            rc = stdout.channel.recv_exit_status()
        except Exception as e:
            error = "Failed to get exit status for command: '{}'.".format(command)
            print(colored(error, 'red'))
            print(colored('Exception:', 'red'))
            print(colored(str(e), 'red'))
            rc = 2
        
        cmdAttrs.append(rc)

        cmdOutput = stdout.read().splitlines()
        for line in cmdOutput:
            outputLine = line.decode()
            cmdOutputList.append(outputLine)
        
        cmdAttrs.append(cmdOutputList)
        return cmdAttrs
    except KeyboardInterrupt as ki:
        error = 'User initiated a Keyboard Interrupt... Quiting....'
        print(error)
        exit(1)
    except Exception as e:
        error = "Unable to connect to and run requested commands on server: '{}'.".format(ssh_client)
        print(colored(error, 'red'))
        print(colored('Exception:', 'red'))
        print(colored(str(e), 'red'))
        return [2, None]
    finally:
        ssh_client.close()


def checkDestinationPortConn(source_conn, source_host, dest_host, protocol, dest_port, quiet):
    conn_check = False
    dns_failure = False
    if protocol == 'tcp':
        command = 'nc -vz {} {} -w 5'.format(dest_host, dest_port)
    elif protocol == 'udp':
        command = 'nc -vzu {} {} -w 5'.format(dest_host, dest_port)
    elif protocol == 'icmp':
        command = 'ping -c3 {}'.format(dest_host)
    
    if protocol == 'tcp' or protocol == 'udp':
        if not quiet:
            print("Testing {} connection from: '{}' to: '{}' on port: '{}'.".format(protocol.upper(), source_host, dest_host, dest_port))
    elif protocol == 'icmp':
        if not quiet:
            print("Testing {} connection from: '{}' to: '{}'.".format(protocol.upper(), source_host, dest_host))

    try:
        commandAttrsList = runCmdOnClient(source_conn, command)
        commandRC = commandAttrsList[0]
        commandOutput = commandAttrsList[1]
    except KeyboardInterrupt as ki:
        error = 'User initiated a Keyboard Interrupt... Quiting....'
        print(error)
        exit(1)
    except Exception as e:
        error = 'Failed to execute command: "{}" on host: "{}".'.format(command, source_host)
        print(colored(error, 'red'))
        print(colored('Exception:', 'red'))
        print(colored(str(e), 'red'))
        commandRC = 2
    finally:
        source_conn.close()
    
    try:
        if commandRC == 0:
            conn_check = True
        else:
            conn_check = False
        
        if commandRC != 0 and (protocol == 'tcp' or protocol == 'udp'):
            if type(commandOutput) == list:
                for line in commandOutput:
                    if 'could not resolve hostname' in line.lower():
                        dns_failure = True
                        break
            else:
                if commandOutput != None:
                    if 'could not resolve hostname' in commandOutput.lower():
                        dns_failure = True

        
        elif commandRC != 0 and protocol == 'icmp':
            for line in commandOutput:
                if 'name or service not known' in line.lower():
                    dns_failure = True
                    break
        
        if conn_check and not dns_failure:
            cprint("{} Connection from: '{}' to: '{}' on port: '{}' Succeeded!".format(protocol.upper(), source_host, dest_host, dest_port), 'green', attrs=['bold'])
        elif dns_failure:
            cprint("Could not resolve destination node: '{}' ".format(dest_host), 'yellow', attrs=['bold'])
        else:
            cprint("{} Connection from: '{}' to: '{}' on port: '{}' Failed!".format(protocol.upper(), source_host, dest_host, dest_port), 'red', attrs=['bold'])
    except KeyboardInterrupt as ki:
        error = 'User initiated a Keyboard Interrupt... Quiting....'
        print(error)
        exit(1)
    except Exception as e:
        error = 'Failed to parse command output for: "{}" on host: "{}".'.format(command, source_host)
        print(colored(error, 'red'))
        print(colored('Exception:', 'red'))
        print(colored(str(e), 'red'))

# Parse arguments
'''
    -P    proxy (default is: nlup-unixmgt01)
    -s    source host (the source host that connection is tested from -> destination host)
    -d    destination host (the source host will test connection on a specific port to the destination host)
    -p    port (the port that the source host will test connection to the destination host)
    -t    protocol type (protocol used to test the connection between source -> destination. Default is: tcp)
    -u    user (Kerberos user used to login to the proxy and the host)
    -a    auth file (full file path of file that contains the Kerberos username and password, in the format: <user>:<password>)
    -q    quiet (setting this will run the script in 'quiet' mode, only showing the result of the connection attempt.)
    -h    help (help menu will be desplayed)
'''

protocol_options = ['tcp', 'udp', 'icmp']
parser = argparse.ArgumentParser(description='Python script that checks network connectivity (using netcat) between two hosts, using a proxy jump host, to get to the source host.')
parser.add_argument('-P', '--proxy', help='The proxy jump host used to connect to the source host.', required=False, default='nlup-unixmgt01', dest='proxy')
parser.add_argument('-s', '--source', help='A ssh connection is established to the source host via the proxy.', required=True, dest='source')
parser.add_argument('-d', '--destination', help='Network connection is tested from the source host to this destination host.', required=True, dest='destination')
parser.add_argument('-p', '--port', help='The network port that should be tested.', required=False, dest='port')
parser.add_argument('-t', '--protocol', help="What network protocol should be tested? Default is 'tcp.'", choices=protocol_options, required=False, default='tcp', dest='protocol')
parser.add_argument('-a', '--authfile', help="Location of the authfile containing credentials of the Kerberos user, in format: <user>:<password>", required=False, dest='authfile')
parser.add_argument('-u', '--user', help='The Kerberos user used to connect to the proxy host as well as the source host.', required=False, dest='user')
parser.add_argument('-q', '--quiet', help="Setting this runs the script in 'quiet' mode, only showing the result of the connection attempt.", required=False, action='store_true', dest='quiet')
args = parser.parse_args()

if (args.protocol == 'tcp' or args.protocol == 'udp') and not args.port:
    print(colored('you need to specify a port to test a tcp or udp connection.', 'red'))
    print(colored('you ONLY do not need to specifiy a port when testing a ping connection.', 'red'))
    parser.print_help()
    exit(1)
if args.authfile:
    try:
        authfile_stats = os.stat(args.authfile)
        authfile_mode = int(oct(authfile_stats.st_mode)[-3:])
    except Exception as e:
        error = 'Failed to determine Auth file mode.'
        print(colored(error, 'red'))
        print(colored('Exception:', 'red'))
        print(colored(str(e), 'red'))
        exit(1)
    if authfile_mode != 600:
        print(colored("Fix Auth file permissions, it should be: '600'.", 'red'))
        exit(1)
    
    auth_file = open(args.authfile, 'r')
    auth_file_contents = auth_file.readline()
    if ':' not in auth_file_contents:
        print(colored('Auth file must be in the format: <username>:<password>.', 'red'))
        exit(1)
    
    user = auth_file_contents.split(':')[0].strip()
    pwd = auth_file_contents.split(':')[1].strip()
    auth_file.close()
else:
    if not args.user:
        print(colored('You must specify a Kerberos user to use.', 'red'))
        parser.print_help()
        exit(1)
    user = args.user
    pwd = getpass.getpass("Enter Kerberos password for '{}': ".format(args.user), stream=None)

try:
    source_ssh_conn = getSSHConnection(args.proxy, args.source, user, pwd, args.quiet)
    if source_ssh_conn:
        checkDestinationPortConn(source_ssh_conn, args.source, args.destination, args.protocol, args.port, args.quiet)
    else:
        print(colored("Failed to establish connection to: '{}', Exiting.".format(args.source), 'red'))
        exit(2)
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
