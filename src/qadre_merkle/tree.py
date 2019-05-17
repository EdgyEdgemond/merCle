#!/usr/bin/env python
from hashlib import sha256

from _merkle import ffi
from _merkle import lib


class MerkleTree:
    @classmethod
    def new(cls, leaves=None, hashed=False):
        if leaves is None:
            leaves = []

        if not hashed:
            leaves = [sha256(leaf).digest() for leaf in leaves]

        leaf_count = len(leaves)
        leaves = [ffi.new("char[]", leaf) for leaf in leaves]
        tree = lib.new_tree(leaves, leaf_count)
        return cls(tree)

    def __init__(self, tree):
        self._tree = tree

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        # Success == 0
        return not lib.compare(self._tree, other._tree)

    def add(self, leaf, hashed=False):
        length = len(leaf)
        leaf = ffi.new("char[]", leaf)
        return lib.add_leaf(self._tree, leaf, length, hashed)

    def update(self, leaf, index, hashed=False):
        length = len(leaf)
        leaf = ffi.new("char[]", leaf)
        status = lib.update_leaf(self._tree, leaf, index, length, hashed)

        if status != 0:
            raise IndexError("assignment index out of range")

    def remove(self, index):
        status = lib.remove_leaf(self._tree, index)

        if status == 1:
            raise IndexError("pop index out of range")

        if status == 2:
            raise IndexError("pop from empty list")

    @property
    def root(self):
        return ffi.buffer(lib.get_root(self._tree), 32)[:]
