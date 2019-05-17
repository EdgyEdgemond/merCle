import random
from hashlib import sha256
from math import log
from math import log2
from uuid import uuid4

import pytest

from mercle.tree import MerkleTree


BOOL = b"\x01"
INT = b"\x02"
UTF8 = b"\x03"
BYTES = b"\x04"


LEAF_COUNTS = [1, 2, 8, 32, 256, 1024, 32768, 65536]


def digest_primitive(obj):
    if isinstance(obj, bool):
        return BOOL + (b"\x01" if obj else b"\x00")

    elif isinstance(obj, int):
        return INT + obj.to_bytes(8, "big", signed=True)

    elif isinstance(obj, str):
        return UTF8 + len(obj).to_bytes(4, "big") + obj.encode()

    elif isinstance(obj, bytes):
        return BYTES + len(obj).to_bytes(4, "big") + obj


def digest(value):
    return sha256(digest_primitive(value)).digest()


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_merkle_add_N_hashed_leaves(benchmark, count):
    def internal():
        m = MerkleTree.new([])
        for _ in range(count):
            m.add(digest(uuid4().hex), True)

    benchmark(internal)


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_merkle_add_N_unhashed_leaves(benchmark, count):
    def internal():
        m = MerkleTree.new([])
        for _ in range(count):
            m.add(digest_primitive(uuid4().hex))

    benchmark(internal)


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_merkle_update_with_N_starting_leaves(benchmark, count):
    leaves = [digest(uuid4().hex) for _ in range(count)]
    m = MerkleTree.new(leaves=leaves)

    benchmark(m.update, digest(uuid4().hex), random.randint(0, count - 1))
#
#
# @pytest.mark.parametrize("count", LEAF_COUNTS)
# def test_merkle_get(benchmark, count):
#     leaves = [digest(uuid4().hex) for _ in range(count)]
#     m = MerkleTree.new(leaves=leaves)
#
#     benchmark(m._get, random.randint(0, count - 1), 0)
#
#
# @pytest.mark.parametrize("count", LEAF_COUNTS)
# def test_merkle_get_sibling(benchmark, count):
#     leaves = [digest(uuid4().hex) for _ in range(count)]
#     m = MerkleTree.new(leaves=leaves)
#
#     benchmark(m._get_sibling, random.randint(0, count - 1), 0)
#
#
# @pytest.mark.parametrize("count", LEAF_COUNTS)
# def test_merkle_update_byte_string(benchmark, count):
#     leaves = [digest(uuid4().hex) for _ in range(count)]
#     m = MerkleTree.new(leaves=leaves)
#
#     benchmark(m._update_byte_string, m.levels[0], digest(uuid4().hex), random.randint(0, count - 1))
#
#
# @pytest.mark.parametrize("count", LEAF_COUNTS)
# def test_merkle_update_level(benchmark, count):
#     leaves = [digest(uuid4().hex) for _ in range(count)]
#     m = MerkleTree.new(leaves=leaves)
#
#     benchmark(m._update_level, digest(uuid4().hex), random.randint(0, count - 1), 0)
#
#
# @pytest.mark.parametrize("count", [2, 8, 32, 256, 1024, 32768, 65536])
# def test_merkle_update_parent(benchmark, count):
#     leaves = [digest(uuid4().hex) for _ in range(count)]
#     m = MerkleTree.new(leaves=leaves)
#
#     benchmark(m._update_parent, digest(uuid4().hex), random.randint(0, count - 1), 0, False)
#
#
# @pytest.mark.parametrize("count", [2, 8, 32, 256, 1024, 32768, 65536])
# def test_merkle_update_parent_recurse(benchmark, count):
#     leaves = [digest(uuid4().hex) for _ in range(count)]
#     m = MerkleTree.new(leaves=leaves)
#
#     benchmark(m._update_parent, digest(uuid4().hex), random.randint(0, count - 1), 0, True)
#
#
# @pytest.mark.parametrize("count", [8, 32, 256, 1024, 32768, 65536])
# def test_merkle_rebuild_level_early_key(benchmark, count):
#     leaves = [digest(uuid4().hex) for _ in range(count)]
#     m = MerkleTree.new(leaves=leaves)
#
#     benchmark(m._rebuild_level, random.randint(0, count / 4), count, 0)
#
#
# @pytest.mark.parametrize("count", [8, 32, 256, 1024, 32768, 65536])
# def test_merkle_rebuild_level_mid_key(benchmark, count):
#     leaves = [digest(uuid4().hex) for _ in range(count)]
#     m = MerkleTree.new(leaves=leaves)
#
#     benchmark(m._rebuild_level, random.randint(count / 4, count / 2), count, 0)
#
#
# @pytest.mark.parametrize("count", [8, 32, 256, 1024, 32768, 65536])
# def test_merkle_rebuild_level_late_key(benchmark, count):
#     leaves = [digest(uuid4().hex) for _ in range(count)]
#     m = MerkleTree.new(leaves=leaves)
#
#     benchmark(m._rebuild_level, random.randint(3 * (count / 4), count - 1), count, 0)
#
#
# def test_merkle_combine(benchmark):
#     m = MerkleTree()
#
#     benchmark(m._combine, digest(uuid4().hex), digest(uuid4().hex))
#
#
# @pytest.mark.parametrize("count", [2, 8, 32, 256, 1024, 32768, 65536])
# def test_log(benchmark, count):
#     benchmark(log, count)
#
#
# @pytest.mark.parametrize("count", [2, 8, 32, 256, 1024, 32768, 65536])
# def test_log2(benchmark, count):
#     benchmark(log2, count)
#
#
# @pytest.mark.parametrize("count", [2, 8, 32, 256, 1024, 32768, 65536])
# def test_log_bit_length(benchmark, count):
#     benchmark(count.bit_length)
