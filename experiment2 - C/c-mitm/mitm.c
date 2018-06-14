
// Server side C/C++ program to demonstrate Socket programming
#define _GNU_SOURCE
#include <unistd.h>
#include <stdio.h>
#include <sched.h>
#include <sys/socket.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <netinet/in.h>
#include <string.h>
#include "tsc.h"
#include <errno.h>
#include <fcntl.h>
#define LISTEN_PORT 8080
#define SERVER_PORT 4040
#define BUFFSIZE 2048
#define LVALUE 16


float median(uint64_t x[]) {
    uint64_t temp;
    uint64_t i, j;
    // the following two loops sort the array x in ascending order
    for(i=0; i<LVALUE-1; i++) {
        for(j=i+1; j<LVALUE; j++) {
            if(x[j] < x[i]) {
                // swap elements
                temp = x[i];
                x[i] = x[j];
                x[j] = temp;
            }
        }
    }

    if(LVALUE%2==0) {
        // if there is an even number of elements, return mean of the two elements in the middle
        return((x[LVALUE/2] + x[LVALUE/2 - 1]) / 2.0);
    } else {
        // else return the element in the middle
        return x[LVALUE/2];
    }
}


void update_delta(int* delta6, int* delta7)
    {
    
        
        if(*delta6 == 255 && *delta7 == 255)
        {
            printf("DONE");
            exit(0);
        }
        else if (*delta6 == 255)
        {
            *delta7 = *delta7 + 1;
            *delta6 = 0;
        }
        else
        {
            *delta6 = *delta6 + 1;
            printf("%d, %d\n", *delta6, *delta7);
        }
        return;
    }
    
int handle_message(char* data, int delta6, int delta7, int message_length)
    {
    
              	//for(int i = 0; i < message_length; i++)
          	     //   printf("%x ", (unsigned char)data[i]);
          	     //printf("\n");
        
        //Get first 5 bytes header
        //Check if first byte is 17, else return
        //Split remaining bytes into blocks of 8
        //XOR last 2 bytes of second to last block with delta values
        
        if((unsigned char)data[0] != 23)
        {
            return 0;
        }

          	for(int i = 5; i < message_length; i += 8){
          	    if(i == message_length - 16)
          	    {
          	        data[i+6] = (unsigned char)data[i+6] ^ (unsigned char)delta6;
          	        data[i+7] = (unsigned char)data[i+7] ^ (unsigned char)delta7;
          	    }
			}
            //printf("\n");
        
        return 1;
    }



int main(int argc, char const *argv[])
{

	cpu_set_t cpuset;
	CPU_ZERO(&cpuset);
	CPU_SET(3, &cpuset);
	sched_setaffinity(0, sizeof(cpu_set_t), &cpuset);
	setpriority(PRIO_PROCESS, 0, -20);
	
	
	
	uint64_t timestamp, start, end, overhead = 0;
	uint64_t timestamp_array[LVALUE] = {0};
    int listen_fd, client_socket, target_fd, target_connected, delta6, delta7, lcount = 0;
    struct sockaddr_in source_address;
	struct sockaddr_in target_address;
    int opt = 1;
    
    int addrlen = sizeof(source_address);
    char data_from_client[BUFFSIZE] = {0};
    char data_from_server[BUFFSIZE] = {0};
    char *c = data_from_client;
    char *s = data_from_server;
    FILE* f = fopen("log", "w");
	  
	fd_set readfds;
	fd_set writefds;
	
	
    source_address.sin_family = AF_INET;
    source_address.sin_addr.s_addr = INADDR_ANY; //localhost
    source_address.sin_port = htons( LISTEN_PORT );
	
	target_address.sin_family = AF_INET;
	target_address.sin_addr.s_addr = INADDR_ANY;
	target_address.sin_port = htons ( SERVER_PORT ); 
	
    // Creating socket file descriptor
    if ((listen_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) //tcp ip ipv4
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }
      
    // Forcefully attaching socket to the port 8080
    if (setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT,
                                                  &opt, sizeof(opt)))
    {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
	
    
      
    // Forcefully attaching socket to the port 8080
    if (bind(listen_fd, (struct sockaddr *)&source_address, 
                                 sizeof(source_address))<0)
    {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
	

	
	for(;;) {
		//Reset bools and ints for the specific client that has connected.
		
		
		if(lcount == LVALUE)
		{
		
            fprintf(f, "%d,%d-%ld\n", delta6, delta7, (long)median(timestamp_array));
            fflush(f);
		    update_delta(&delta6, &delta7);
		    lcount = 0;
		}
		
		
		
    	int message_for_server, message_for_client, badmac = 0;
    	int total_received_from_server, total_received_from_client = 0;
    	
        memset(data_from_server, 0, sizeof(data_from_server));
        memset(data_from_client, 0, sizeof(data_from_client));
            
        	// Creating socket file descriptor to server
    if ((target_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) //tcp ip ipv4
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    } 
            	
		//connection to client
		if (listen(listen_fd, 2) < 0)
		{
			perror("listen");
			exit(EXIT_FAILURE);
		}

		if ((client_socket = accept(listen_fd, (struct sockaddr *)&source_address, 
                       (socklen_t*)&addrlen))<0)
		{
			perror("accept");
			exit(EXIT_FAILURE);
		}
		
		if(target_connected == 0){
			//connection to target server
			
			target_connected = 1;
			
		
			
			if (connect(target_fd, (struct sockaddr *)&target_address, sizeof(target_address)) < 0)
			{
				printf("\nConnection to server Failed \n");
				return -1;
			}

		}
		
		for(;;) {
			//Reset variables
			int count, valread = 0;
			int max_sd, activity = 0;
			
			//Zero the select sets
        	FD_ZERO(&readfds);
        	FD_ZERO(&writefds);
        	//Tell select which file descriptors to look at
        	FD_SET(target_fd, &readfds);
        	FD_SET(client_socket, &readfds);
        	FD_SET(target_fd, &writefds);
        	FD_SET(client_socket, &writefds);        	
        	max_sd = client_socket;

			//Block here till a file descriptor either has data waiting to be recieved, or is ready to send data. 
        	activity = select( max_sd + 1 , &readfds , &writefds , NULL , NULL);
        	
        	if (FD_ISSET( client_socket , &readfds)) 
            {
            	
            	memset(data_from_client, 0, sizeof(data_from_client));
                //Check if it was for closing , and also read the incoming message
                if ((count = recv( client_socket , data_from_client, BUFFSIZE, 0)) == 0)
                {
                	
                	close( client_socket );
                    
                    target_connected = 0;
                    //fprintf(stderr, "recv: %s (%d)\n", strerror(errno), errno);
                    break;
                }
                  
                //Echo back the message that came in
                else
                {
                    message_for_server = 1;
                    total_received_from_client += count;
                       
                    continue;
                }
            }
        	if (FD_ISSET( target_fd , &readfds)) 
            {
                if(badmac)
                    {
                    	end = bench_end();
                        timestamp = end - start - overhead;
                        timestamp_array[lcount] = timestamp;
                        lcount++;
                        //printf("%d,%d-%ld\n", delta6, delta7, (long)timestamp);
                        badmac = 0;
                    }
            	
                //Check if it was for closing , and also read the incoming message
                if ((count = recv( target_fd , data_from_server, BUFFSIZE, 0)) == 0)
                {
               	    close( target_fd );
                    target_connected = 0;
                }
                  
                //Echo back the message that came in
                else
                {   

                    
                    message_for_client = 1;
                    total_received_from_server += count;
                    continue;
                }
            }
            
            if (FD_ISSET( target_fd , &writefds) && message_for_server)
            {
                    
		badmac = handle_message(data_from_client, 1, 1, total_received_from_client);
		if(badmac)
		{
			overhead = measure_tsc_overhead();
			start = bench_start();
		}  
            	send(target_fd , data_from_client , total_received_from_client , 0 );
            	message_for_server = 0;
            	total_received_from_client = 0;
            }
            
            if (FD_ISSET( client_socket , &writefds) && message_for_client)
            {
            	send(client_socket , data_from_server , total_received_from_server , 0 );
            	memset(data_from_server, 0, sizeof(data_from_server));
            	message_for_client = 0;
            	total_received_from_server = 0;
            }
		}
	}
    fclose(f);
    return 0;
    
	
}




