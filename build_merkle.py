#!/usr/bin/env python
import os

import cffi


ffi = cffi.FFI()

ffi.set_source(
    "_merkle",
    # Since we are calling a fully built library directly no custom source
    # is necessary. We need to include the .h files, though, because behind
    # the scenes cffi generates a .c file which contains a Python-friendly
    # wrapper around each of the functions.
    '#include "merkle.h"',
    # The important thing is to include the pre-built lib in the list of
    # libraries we are linking against:
    libraries=["merkle"],
    library_dirs=[os.path.dirname(__file__)],
    extra_link_args=["-Wl,-rpath=./"],
)

with open(os.path.join(os.path.dirname(__file__), "merkle.h")) as f:
    ffi.cdef(f.read())

if __name__ == "__main__":

    ffi.compile()
