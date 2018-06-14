#!/usr/bin/env  python2
import argparse
import pkgutil
import os
import sys
import socket
import ssl
import time
import select
import errno
import time
import fau_timer
# TODO: implement verbose output
# some code snippets, as well as the original idea, from Black Hat Python


def is_valid_ip4(ip):
    # some rudimentary checks if ip is actually a valid IP
    octets = ip.split('.')
    if len(octets) != 4:
        return False
    return octets[0] != 0 and all(0 <= int(octet) <= 255 for octet in octets)


def parse_args():
    parser = argparse.ArgumentParser(description='Simple TCP proxy for data ' +
                                                 'interception and ' +
                                                 'modification. ' +
                                                 'Select modules to handle ' +
                                                 'the intercepted traffic.')

    parser.add_argument('-ti', '--targetip', dest='target_ip',
                        help='remote target IP or host name')

    parser.add_argument('-tp', '--targetport', dest='target_port', type=int,
                        help='remote target port')

    parser.add_argument('-li', '--listenip', dest='listen_ip',
                        default='0.0.0.0', help='IP address/host name to listen for ' +
                        'incoming data')

    parser.add_argument('-lp', '--listenport', dest='listen_port', type=int,
                        default=8080, help='port to listen on')

    parser.add_argument('-om', '--outmodules', dest='out_modules',
                        help='comma-separated list of modules to modify data' +
                             ' before sending to remote target.')

    parser.add_argument('-im', '--inmodules', dest='in_modules',
                        help='comma-separated list of modules to modify data' +
                             ' received from the remote target.')

    parser.add_argument('-v', '--verbose', dest='verbose', default=False,
                        action='store_true',
                        help='More verbose output of status information')

    parser.add_argument('-n', '--no-chain', dest='no_chain_modules',
                        action='store_true', default=False,
                        help='Don\'t send output from one module to the ' +
                             'next one')

    parser.add_argument('-l', '--log', dest='logfile', default=None,
                        help='Log all data to a file before modules are run.')

    parser.add_argument('--list', dest='list', action='store_true',
                        help='list available modules')

    parser.add_argument('-lo', '--list-options', dest='help_modules', default=None,
                        help='Print help of selected module')

    parser.add_argument('-s', '--ssl', dest='use_ssl', action='store_true',
                        default=False, help='detect SSL/TLS as well as STARTTLS, certificate is mitm.pem')

    return parser.parse_args()


def generate_module_list(modstring, incoming=False, verbose=False):
    # This method receives the comma-separated module list, imports the modules
    # and creates a Module instance for each module. A list of these instances
    # is then returned.
    # The incoming parameter is True when the modules belong to the incoming
    # chain (-im)
    # modstring looks like mod1,mod2:key=val,mod3:key=val:key2=val2,mod4 ...
    modlist = []
    namelist = modstring.split(',')
    for n in namelist:
        name, options = parse_module_options(n)
        try:
            __import__('proxymodules.' + name)
            modlist.append(sys.modules['proxymodules.' + name].Module(incoming, verbose, options))
        except ImportError:
            print 'Module %s not found' % name
            sys.exit(3)
    return modlist


def parse_module_options(n):
    # n is of the form module_name:key1=val1:key2=val2 ...
    # this method returns the module name and a dict with the options
    n = n.split(':', 1)
    if len(n) == 1:
        # no module options present
        return n[0], None
    name = n[0]
    optionlist = n[1].split(':')
    options = {}
    for op in optionlist:
        try:
            k, v = op.split('=')
            options[k] = v
        except ValueError:
            print op, ' is not valid!'
            sys.exit(23)
    return name, options




def update_module_hosts(modules, source, destination):
    # set source and destination IP/port for each module
    # source and destination are ('IP', port) tuples
    # this can only be done once local and remote connections have been established
    if modules is not None:
        for m in modules:
            if hasattr(m, 'source'):
                m.source = source
            if hasattr(m, 'destination'):
                m.destination = destination


def receive_from(s):
    # receive data from a socket until no more data is there
    b = ""
    while True:
        data = s.recv(4096)
        b += data
        if not data or len(data)<4096:
            break
    return b


def handle_data(data, modules, dont_chain, incoming, verbose, delta_6, delta_7):
    # execute each active module on the data. If dont_chain is set, feed the
    # output of one plugin to the following plugin. Not every plugin will
    # necessarily modify the data, though.
    for m in modules:
        if verbose:
            print ("> > > > in: " if incoming else "< < < < out: ") + m.name
        if dont_chain:
            m.execute(data)
        else:
            data, log_time = m.execute(data, delta_6, delta_7)
    return data, log_time


def is_client_hello(sock):
    firstbytes = sock.recv(128, socket.MSG_PEEK)
    return (len(firstbytes) >= 3 and
            firstbytes[0] == "\x16" and
            firstbytes[1:3] in [ "\x03\x00",
                                 "\x03\x01",
                                 "\x03\x02",
                                 "\x03\x03",
                                 "\x02\x00", ]
        )


def enable_ssl(remote_socket, local_socket):
    local_socket = ssl.wrap_socket(local_socket,
                server_side=True,
                certfile="mitm.pem",
                keyfile="mitm.pem",
                #ssl_version=ssl.PROTOCOL_TLS,
              )

    remote_socket = ssl.wrap_socket(remote_socket)
    return [remote_socket, local_socket]


def starttls(args, local_socket, read_sockets):
    return (args.use_ssl and
        local_socket in read_sockets and
        not isinstance(local_socket, ssl.SSLSocket) and
        is_client_hello(local_socket)
       )
    
def handle_connection(local_socket, args, in_modules, out_modules, delta_6, delta_7):
    # This method is executed in a thread. It will relay data between the local
    # host and the remote host, while letting modules work on the data before
    # passing it on.
    remote_socket = socket.socket()
    global time_array
    #

    try:
        remote_socket.connect((args.target_ip, args.target_port))
        if args.verbose:
            print 'Connected to %s:%d' % remote_socket.getpeername()
        log(args.logfile, 'Connected to %s:%d' % remote_socket.getpeername())
    except socket.error as serr:
        if serr.errno == errno.ECONNREFUSED:
            print '%s:%d - Connection refused' % (args.target_ip, args.target_port)
            log(args.logfile, '%s:%d - Connection refused' % (args.target_ip, args.target_port))
            return None
        else:
            raise serr

    update_module_hosts(out_modules, local_socket.getpeername(), remote_socket.getpeername())
    update_module_hosts(in_modules, remote_socket.getpeername(), local_socket.getpeername())

    sendBrokenMessageTicks = None
    # This loop ends when no more data is received on either the local or the
    # remote socket
    log_time = False
    running = True
    while running:
        read_sockets, _, _ = select.select([remote_socket, local_socket], [], [])
        
        for sock in read_sockets:
            peer = sock.getpeername()
            data = receive_from(sock)
	    
            if sock == remote_socket and sendBrokenMessageTicks is not None and log_time: #if we have previously sent modified message, we want to see how loong it took to respond

                errorTime = fau_timer.get_ticks() - sendBrokenMessageTicks
                sendBrokenMessageTicks = None
                #save this errorTime to some file
                #also write delta

                time_array.append(errorTime)

		#STOP = 'bad record mac'
		#local_socket.send(STOP)
		local_socket.close()
		remote_socket.close()
                return
                #log(timeLog, str(delta_6) + ", " + str(delta_7) + " - ", message_only=True)
                #log(timeLog, str(errorTime) + '\n', message_only=True)
                
            log(args.logfile, 'Received %d bytes' % len(data))

            if sock == local_socket: #client?
                if len(data):
                    log(args.logfile, '< < < out\n' + data)
                    if out_modules is not None:
                        data, log_time = handle_data(data, out_modules,
                                           args.no_chain_modules,
                                           False,  # incoming data?
                                           args.verbose,
                                           delta_6, delta_7)
                    sendBrokenMessageTicks = fau_timer.get_ticks() #now we have sent a modified message
                    remote_socket.send(data)
                else:
                    if args.verbose:
                        print "Connection from local client %s:%d closed" % peer
                    log(args.logfile, "Connection from local client %s:%d closed" % peer)
                    remote_socket.close()
                    running = False
                    break
            elif sock == remote_socket:
                if len(data):
                    log(args.logfile, '> > > in\n' + data)
                    if in_modules is not None:
                        data, log_time = handle_data(data, in_modules,
                                           args.no_chain_modules,
                                           True,  # incoming data?
                                           args.verbose,
                                           None, None)
                    local_socket.send(data)
                else:
                    if args.verbose:
                        print "Connection to remote server %s:%d closed" % peer
                    log(args.logfile, "Connection to remote server %s:%d closed" % peer)
                    local_socket.close()
                    running = False
                    break


def log(handle, message, message_only=False):
    # if message_only is True, only the message will be logged
    # otherwise the message will be prefixed with a timestamp and a line is
    # written after the message to make the log file easier to read
    if handle is None:
        return
    if not message_only:
        logentry = "%s %s\n" % (time.strftime('%Y%m%d-%H%M%S'),
                                 str(time.time()))
    else:
        logentry = ''
    logentry += message
    if not message_only:
        logentry += '\n' + '-' * 20 + '\n'
    handle.write(logentry)

def update_delta(delta_6, delta_7):
    if delta_6 == 255 and delta_7 == 255:
        print "DONE"
        sys.exit(0)
    if delta_6 == 255:
        delta_7 += 1
        delta_6 = 0
    else:
        delta_6 += 1
    return delta_6, delta_7
    
time_array = []     
    
def main():
    args = parse_args()
    if args.list is False and args.help_modules is None:
        if not args.target_ip:
            print 'Target IP is required: -ti'
            sys.exit(6)
        if not args.target_port:
            print 'Target port is required: -tp'
            sys.exit(7)

    if args.logfile is not None:
        try:
            args.logfile = open(args.logfile, 'a', 0)  # unbuffered
        except Exception as ex:
            print 'Error opening logfile'
            print ex
            sys.exit(4)

    

    if args.listen_ip != '0.0.0.0' and not is_valid_ip4(args.listen_ip):
        try:
            ip = socket.gethostbyname(args.listen_ip)
        except socket.gaierror:
            ip = False
        if ip is False:
            print '%s is not a valid IP address or host name' % args.listen_ip
            sys.exit(1)
        else:
            args.listen_ip = ip

    if not is_valid_ip4(args.target_ip):
        try:
            ip = socket.gethostbyname(args.target_ip)
        except socket.gaierror:
            ip = False
        if ip is False:
            print '%s is not a valid IP address or host name' % args.target_ip
            sys.exit(2)
        else:
            args.target_ip = ip

    if args.in_modules is not None: #modules for communication from client (incoming)
        in_modules = generate_module_list(args.in_modules, incoming=True, verbose=args.verbose)
    else:
        in_modules = None

    if args.out_modules is not None: #modules for communication from server (outgoing)
        out_modules = generate_module_list(args.out_modules, incoming=False, verbose=args.verbose)
    else:
        out_modules = None

    # this is the socket we will listen on for incoming connections
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        proxy_socket.bind((args.listen_ip, args.listen_port))
    except socket.error as e:
        print e.strerror
        sys.exit(5)

    fau_timer.init()
    timeLog = open("timeLog", 'a', 0)
    delta_6 = 0 #1
    delta_7 = 1 #0
    L = 4
    counter = 0
    global time_array
    proxy_socket.listen(10)
    log(args.logfile, str(args))
    # endless loop until ctrl+c
    try:
        while True:
	    
            in_socket, in_addrinfo = proxy_socket.accept() #this method waits for an incoming connection - returns when this happens, o.w. waits
            
            if counter == L:
                counter = 0
                errorTime = median(time_array)
                log(timeLog, str(delta_6) + "," + str(delta_7) + "-", message_only=True)
                log(timeLog, str(errorTime) + '\n', message_only=True)
                delta_6, delta_7 = update_delta(delta_6, delta_7)
                time_array = []
            else: 
                counter = counter + 1
                
            if args.verbose:
                print 'Connection from %s:%d' % in_addrinfo
            log(args.logfile, 'Connection from %s:%d' % in_addrinfo)
            #proxy_thread = threading.Thread(target=handle_connection,
                                           # args=(in_socket, args, in_modules,
                                            #      out_modules, delta_6, delta_7))
            #log(args.logfile, "Starting proxy thread " + proxy_thread.name)
            #proxy_thread.start()
            
            handle_connection(in_socket, args, in_modules, out_modules, delta_6, delta_7)
    except KeyboardInterrupt:
        log(args.logfile, 'Ctrl+C detected, exiting...')
        print '\nCtrl+C detected, exiting...'
        sys.exit(0)

def median(lst):
    n = len(lst)
    if n < 1:
            return None
    if n % 2 == 1:
            return sorted(lst)[n/2]
    else:
            return sum(sorted(lst)[n/2-1:n/2+1])/2.0



if __name__ == '__main__':
    main()
