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
    
    
    command = "/usr/local/ssl/bin/openssl s_client -connect " + args.listen_ip + ":" + str(args.listen_port) 
    #print(command)
    count = 0
    while(count < 65535): #65535
	    cmd = pexpect.spawn(command) 

	    cmd.expect('Verify return code')
	    
	    cmd.sendline('Lorem ipsum dolor sit amet aenean suscipit.') 
          #'Lorem ipsum dolor sit amet aenean suscipit.' is 43 bytes. With a header of 13, this gives either 57, 56 or 55 bytes to be verified.  
	    #We can try with a 41 byte message, so we can predict maybe which point will be the target delta values?
	    
	    #print(cmd.read())
	    #cmd.expect('bad record mac')
	    cmd.expect(pexpect.EOF)
	    cmd.sendline('Q')
	    cmd.close()
	    count = count +1
    
    
    print("done")
    
