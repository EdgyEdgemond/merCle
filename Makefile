all: clean merkle

clean:
	rm -f *.o *.so _merkle.c

libmerkle.so: merkle.o
	gcc -shared -lssl -lcrypto $^ -o $@

%.o: %.c
	gcc -c -g -Wall -Werror -fpic -lssl -lcrypto $^

merkle: export LD_LIBRARY_PATH = $(shell pwd)
merkle: libmerkle.so
	./build_merkle.py
	# ./testMerkle.py
