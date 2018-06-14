#!/usr/bin/env python2


class Module:
    def __init__(self, incoming=False, verbose=False, options=None):
        # extract the file name from __file__. __file__ is proxymodules/name.py
        self.name = __file__.rsplit('/', 1)[1].split('.')[0]
        self.description = 'Print a hexdump of the received data'
        self.incoming = incoming  # incoming means module is on -im chain
        self.len = 8
        self.delta = [00, 00, 00, 00, 00, 00, 01, 01]
        if options is not None:
            if 'length' in options.keys():
                self.len = int(options['length'])

    def help(self):
        return '\tlength: bytes per line (int)'

    def execute(self, data, delta_6, delta_7):

        digits = 4 if isinstance(data, unicode) else 2
        hexa = []
        self.delta[6] = delta_6
        self.delta[7] = delta_7
        
        first = data[0:5]
        hexa.append(["%0*X" % (digits, ord(x)) for x in first])

	with open("logE.txt", "a") as myfile:
    	    myfile.write(hexa[0][0]+'\n')

	if hexa[0][0] != '17':
	    return data, False

        for i in xrange(5, len(data), self.len):
            s = data[i:i + self.len]
            hexa.append(["%0*X" % (digits, ord(x)) for x in s])

        #at this point hexa contains all our data in arrays corresponding to blocks of encrypted data
        #block 0 is the TLS header
        C_prime = ['0'] * 8
        C = hexa[-2]

        for index in range(self.len):
            C_prime[index] = "%0*X" % (digits, (self.delta[index] ^ int(C[index], 16)))
            
	#print C
        #print C_prime

	hexa[-2] = C_prime
       	#print hexa
        result = ''
            
        for j in hexa:
            d = b''.join(["%s" % (chr(int(x, 16))) for x in j])
            result += d 
        
        #print data
        #print '\n \n'
        #print result
        #print '\n'
        #print data == result
        
	return result, True    
        

if __name__ == '__main__':
    print ('This module is not supposed to be executed alone!')
