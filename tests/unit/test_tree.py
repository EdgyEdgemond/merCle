from hashlib import sha256

import pytest

import mercle.tree


BOOL = b"\x01"
INT = b"\x02"
UTF8 = b"\x03"
BYTES = b"\x04"


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


@pytest.mark.parametrize("data,root_hash,expected_depth", (
    (
        [
            digest("a"),
        ],
        "76b2728fb369947e87e380b2088b064cda198ceb81d7a88ec4f19c87bd65a0b0",
        2,
    ),
    (
        [
            digest("a"),
            digest("b"),
        ],
        "3e98c5cfe0ba9146cb8821f56ec3fec8eec8e563ca81367637faa4425132b117",
        2,
    ),
    (
        [
            digest("a"),
            digest("b"),
            digest("c"),
        ],
        "837451fcbce4c765950482df9d7438b16d60db9b9c8ca45fce752ffcb34a3c00",
        3,
    ),
    (
        [
            digest("a"),
            digest("b"),
            digest("c"),
            digest("d"),
        ],
        "99a0b480387f2c2c97cbce73195bdca3dba8ec148a7ef61689b96569977d587e",
        3,
    ),
    (
        [
            digest("a"),
            digest("b"),
            digest("c"),
            digest("d"),
            digest("e"),
            digest("f"),
        ],
        "e1e81019b77a3ec83a808a50e07e5035c7a261c82b7850bf2e23c7b7a5591ca8",
        4,
    ),
    (
        [
            digest("a"),
            digest("b"),
            digest("c"),
            digest("d"),
            digest("e"),
            digest("f"),
            digest("g"),
            digest("h"),
            digest("i"),
        ],
        "1bfd178b76091323dfac56f4a6211bcff2746ab034149d66b3d1e4ac488ff003",
        5,
    ),
))
def test_elements(data, root_hash, expected_depth):
    m = mercle.tree.MerkleTree.new(leaves=data, hashed=True)
    assert m.root.hex() == root_hash
    # assert len(m.levels) == expected_depth


def test_equality():
    leaves = [digest(value) for value in ["a", "b", "c"]]
    m = mercle.tree.MerkleTree.new(leaves=leaves)
    m2 = mercle.tree.MerkleTree.new(leaves=leaves)

    assert m == m2


def test_empty_equality():
    m = mercle.tree.MerkleTree.new()
    m2 = mercle.tree.MerkleTree.new()

    assert m == m2


def test_add_leaf_to_empty_tree_doesnt_error():
    m = mercle.tree.MerkleTree.new()

    m.add(digest(b"something"), hashed=True)

    m.root == digest(b"something")


def test_empty_hash():
    m = mercle.tree.MerkleTree.new()

    m.root == bytearray(32)


def test_single_leaf():
    m = mercle.tree.MerkleTree.new()

    m.add(digest("a"), hashed=True)
    assert m.root == sha256(digest("a") + bytearray(32)).digest()


def test_delete_all_leaves():
    m = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["one", "two", "three", "four"]],
        hashed=True,
    )

    m.remove(3)
    m.remove(2)
    m.remove(1)
    m.remove(0)

    m.root == bytearray(32)


def test_delete_last_key_with_truncate():
    m = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["one", "two", "three", "four", "five"]],
        hashed=True,
    )

    m.remove(4)

    m.root == b""


def test_update_single_leave_tree():
    m = mercle.tree.MerkleTree.new([digest("something")], hashed=True)

    m.update(digest(b"something"), 0)


def test_update_out_of_range():
    m = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["one", "two", "three", "five", "six"]],
        hashed=True,
    )

    with pytest.raises(IndexError):
        m.update(digest("twenty"), 20)


def test_update_empty():
    m = mercle.tree.MerkleTree.new()

    with pytest.raises(IndexError):
        m.update(digest("twenty"), 20)


def test_remove_out_of_range():
    m = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["one", "two", "three", "five", "six"]],
        hashed=True,
    )

    with pytest.raises(IndexError):
        m.remove(20)


def test_remove_empty():
    m = mercle.tree.MerkleTree.new()

    with pytest.raises(IndexError):
        m.remove(20)


def test_removal_of_leaf_matches_tree_not_containing_leaf():
    m1 = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["one", "two", "three", "five", "six"]],
        hashed=True,
    )
    m2 = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["one", "two", "three", "four", "five", "six"]],
        hashed=True,
    )
    m3 = mercle.tree.MerkleTree.new()

    assert m1.root != m2.root
    assert m1.root != m3.root

    m2.remove(3)
    m3.add(digest("one"), hashed=True)
    m3.add(digest("two"), hashed=True)
    m3.add(digest("three"), hashed=True)
    m3.add(digest("five"), hashed=True)
    m3.add(digest("six"), hashed=True)

    assert m1.root == m2.root
    assert m1.root == m3.root


def test_update_after_remove():
    m1 = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["one", "two", "three", "six"]],
        hashed=True,
    )
    m2 = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["one", "two", "three", "four", "five"]],
        hashed=True,
    )
    m3 = mercle.tree.MerkleTree.new()

    assert m1.root != m2.root
    assert m1.root != m3.root

    m3.add(digest("one"), hashed=True)
    m3.add(digest("two"), hashed=True)
    m3.add(digest("three"), hashed=True)
    m3.add(digest("six"), hashed=True)
    m2.remove(3)
    m2.update(digest("six"), 3, hashed=True)

    assert m1.root == m2.root
    assert m1.root == m3.root


def test_removal_of_leaf_matches_tree_not_containing_leaf_drops_below_power_of_two():
    m1 = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["one", "two", "three", "five"]],
        hashed=True,
    )
    m2 = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["one", "two", "three", "four", "five"]],
        hashed=True,
    )
    m3 = mercle.tree.MerkleTree.new()

    assert m1.root != m2.root
    assert m1.root != m3.root

    m2.remove(3)
    m3.add(digest("one"), hashed=True)
    m3.add(digest("two"), hashed=True)
    m3.add(digest("three"), hashed=True)
    m3.add(digest("five"), hashed=True)

    assert m1.root == m2.root
    assert m1.root == m3.root


def test_removal_of_leaf_matches_tree_not_containing_leaf_truncates_to_one_key():
    m1 = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["one"]],
        hashed=True,
    )
    m2 = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["one", "two", "three", "four", "five"]],
        hashed=True,
    )
    m3 = mercle.tree.MerkleTree.new()

    assert m1.root != m2.root
    assert m1.root != m3.root

    m2.remove(3)
    m2.remove(3)
    m2.remove(2)
    m2.remove(1)
    m3.add(digest("one"), hashed=True)

    assert m1.root == m2.root


def test_removal_of_leaf_cleans_orphaned_parents_back_to_null():
    m1 = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]],
        hashed=True,
    )
    m2 = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]],
        hashed=True,
    )
    m3 = mercle.tree.MerkleTree.new()

    assert m1.root != m2.root
    assert m1.root != m3.root

    m2.remove(10)
    for l in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]:
        m3.add(digest(l), hashed=True)

    assert m1.root == m2.root
    assert m1.root == m3.root


def test_append_leaves():
    hashes = [
        "76b2728fb369947e87e380b2088b064cda198ceb81d7a88ec4f19c87bd65a0b0",
        "3e98c5cfe0ba9146cb8821f56ec3fec8eec8e563ca81367637faa4425132b117",
        "837451fcbce4c765950482df9d7438b16d60db9b9c8ca45fce752ffcb34a3c00",
        "99a0b480387f2c2c97cbce73195bdca3dba8ec148a7ef61689b96569977d587e",
    ]

    data = [
        digest("a"),
        digest("b"),
        digest("c"),
        digest("d"),
    ]

    m = mercle.tree.MerkleTree.new(leaves=[data[0]], hashed=True)
    assert m.root.hex() == hashes[0]

    for i in range(1, 4):
        m.add(data[i], hashed=True)

        assert m.root.hex() == hashes[i]


@pytest.mark.skip("test in c")
@pytest.mark.parametrize("leaf_count,base_count", (
    (1, 2),
    (2, 2),
    (3, 4),
    (5, 8),
    (15, 16),
    (21, 32),
    (54, 64),
))
def test_tree_expands_base_level_to_next_power_of_two(leaf_count, base_count):
    data = [digest(l) for l in range(leaf_count)]

    m = mercle.tree.MerkleTree.new(leaves=data)

    assert m._level_size(0) == base_count


def test_marshal_empty_tree():
    mt = mercle.tree.MerkleTree.new()

    payload = mt.marshal()

    assert mercle.tree.MerkleTree.unmarshal(payload) == mt


def test_marshal_tree():
    mt = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]],
    )

    payload = mt.marshal()

    assert mercle.tree.MerkleTree.unmarshal(payload) == mt


def test_get_proof():
    mt = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["a", "b", "c", "d", "e", "f", "g", "h"]],
    )

    sibling = digest("d")
    parent_sibling = sha256(digest("a") + digest("b")).digest()
    grandparent_sibling = sha256(
        sha256(digest("e") + digest("f")).digest() + sha256(digest("g") + digest("h")).digest(),
    ).digest()

    assert mt.get_proof(2) == [
        ["R", sibling],
        ["L", parent_sibling],
        ["R", grandparent_sibling],
        ["ROOT", mt.root],
    ]


def test_get_proof_after_update():
    mt = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["a", "b", "c", "d", "e", "f", "g", "h"]],
    )

    mt.update(digest("z"), 3)

    sibling = digest("z")
    parent_sibling = sha256(digest("a") + digest("b")).digest()
    grandparent_sibling = sha256(
        sha256(digest("e") + digest("f")).digest() + sha256(digest("g") + digest("h")).digest(),
    ).digest()

    assert mt.get_proof(2) == [
        ["R", sibling],
        ["L", parent_sibling],
        ["R", grandparent_sibling],
        ["ROOT", mt.root],
    ]


def test_tree_proof_validates():
    mt = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["a", "b", "c", "d", "e", "f", "g", "h"]],
    )

    proof = mt.get_proof(2)

    assert mercle.util.verify_proof(proof, digest("c")) is True


def test_verify_merkle_proof_invalid():
    mt = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["a", "b", "c", "d", "e", "f", "g", "h"]],
    )

    proof = mt.get_proof(2)

    assert mercle.util.verify_proof(proof, digest("z")) is False


def test_combined_proofs_validates():
    m1 = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["a", "b", "c"]],
    )
    m2 = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["d", "e", "f"]],
    )
    m3 = mercle.tree.MerkleTree.new(
        [digest(value) for value in ["g", "h", "i"]],
    )
    parent = mercle.tree.MerkleTree.new(
        [m1.root, m2.root, m3.root],
    )

    proof_of_e = m2.get_proof(1)
    proof_of_m2 = parent.get_proof(1)

    combined_proof = mercle.util.combine_proofs(proof_of_e, proof_of_m2)

    assert mercle.util.verify_proof(combined_proof, digest("e"))
