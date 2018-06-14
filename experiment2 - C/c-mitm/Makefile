HEADERS = 1
OBJECTS = mitm.o test_server.o test_client.o

default: mitm 

all: test_client test_server

%.o: %.c $(HEADERS)
	gcc -c $< -o $@

program: $(OBJECTS)
	gcc $(OBJECTS) -o $@

clean:
	-rm -f $(OBJECTS)
	-rm -f program
