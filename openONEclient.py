# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 13:21:31 2018

@author: Admin
"""

import argparse
import pexpect

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Client bla bla")

    parser.add_argument('-li', '--listenip', dest='listen_ip',
                        default='0.0.0.0', help='IP address/host name to listen for ' +
                        'incoming data')

    parser.add_argument('-lp', '--listenport', dest='listen_port', type=int,
                        default=8080, help='port to listen on')

    args = parser.parse_args()
    
    
    command = "openssl s_client -connect " + args.listen_ip + ":" + str(args.listen_port) 
    cmd = pexpect.spawn(command) 
    cmd.expect('Verify return code')
    cmd.sendline('Lorem ipsum dolor sit amet, consectetur sed.') #44 bytes lorem ipsum
    
    
    
    
