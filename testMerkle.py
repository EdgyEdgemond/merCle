#!/usr/bin/env python
from hashlib import sha256

from _merkle import ffi
from _merkle import lib

from mercle import tree


if __name__ == "__main__":
    pmt = tree.MerkleTree.new()
    mt = tree.MerkleTree.new()

    print("00:", mt.root.hex(), pmt.root.hex(), mt.root.hex() == pmt.root.hex())
    for i, k in enumerate([b"a", b"b", b"c", b"d", b"e", b"f", b"g", b"h", b"i", b"j", b"k", b"l"]):
        mt.add(k)
        pmt.add(sha256(k).digest(), hashed=True)
        print("{}:".format(i+1).zfill(3), mt.root.hex(), pmt.root.hex(), mt.root.hex() == pmt.root.hex())

    print("="*139)
    # for i in [4, 5, 2, 0]:
    #     mt.remove(i)
    #     pmt.remove(i)
    #     print("{}:".format(i).zfill(3), mt.root.hex(), pmt.root.hex(), mt.root.hex() == pmt.root.hex())

    for i in range(12):
        mt.remove(0)
        pmt.remove(0)
        print("{}:".format(i).zfill(3), mt.root.hex(), pmt.root.hex(), mt.root.hex() == pmt.root.hex())

    # for i in reversed(range(12)):
    #     mt.remove(i)
    #     pmt.remove(i)
    #     print("{}:".format(i).zfill(3), mt.root.hex(), pmt.root.hex(), mt.root.hex() == pmt.root.hex())

    # a = sha256(b"a").digest()
    # b = sha256(b"b").digest()
    # c = sha256(b"c").digest()
    # empty = sha256(bytearray(32)).digest()
    # #
    # # print("a: ", a)
    # # print("a: ", a.hex())
    # # print("b: ", b.hex())
    # # print("c: ", c.hex())
    # # print("empty: ", empty.hex())
    # # print("root: ", tree.root.hex())
    # # print("a + e: ", sha256(a + bytearray(32)).digest().hex())
    # # print("a + b: ", sha256(a + b).digest().hex())
    # # print("c + e: ", sha256(c + bytearray(32)).digest().hex())
    # # print("=" * 64)
    # #
    # mt.add(b"a")
    # pmt.add(a)
    # print("1: ", mt.root.hex(), " ", pmt.root.hex())
    #
    # mt.add(b"b")
    # pmt.add(b)
    # print("2: ", mt.root.hex(), " ", pmt.root.hex())
    # #
    # # mt.update(b"c", 1)
    # # pmt.update(c, 1)
    # # print("2: ", mt.root.hex(), " ", pmt.root.hex())
    #
    # mt.add(b"d")
    # pmt.add(sha256(b"d").digest())
    # print("3: ", mt.root.hex(), " ", pmt.root.hex())
    #
    # mt.add(b"e")
    # pmt.add(sha256(b"e").digest())
    # print("4: ", mt.root.hex(), " ", pmt.root.hex())
    #
    # mt.add(b"f")
    # pmt.add(sha256(b"f").digest())
    # print("5: ", mt.root.hex(), " ", pmt.root.hex())
    #
    # mt.add(b"g")
    # pmt.add(sha256(b"g").digest())
    # print("6: ", mt.root.hex(), " ", pmt.root.hex())
    #
    # mt.remove(5)
    # pmt.remove(5)
    # print("5: ", mt.root.hex(), " ", pmt.root.hex())
    #
    # mt.remove(4)
    # pmt.remove(4)
    # print("3: ", mt.root.hex(), " ", pmt.root.hex())
    #
    # mt.remove(3)
    # pmt.remove(3)
    # print("3: ", mt.root.hex(), " ", pmt.root.hex())
    #
    # mt.remove(2)
    # pmt.remove(2)
    # print("2: ", mt.root.hex(), " ", pmt.root.hex())
    #
    # mt.remove(1)
    # pmt.remove(1)
    # print("1: ", mt.root.hex(), " ", pmt.root.hex())
    #
    # mt.remove(0)
    # pmt.remove(0)
    # print("0: ", mt.root.hex(), " ", pmt.root.hex())
    #
    # tree.remove(0)
    # print(tree.hash().hex())
