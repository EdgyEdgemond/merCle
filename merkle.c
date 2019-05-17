#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>
#include "merkle.h"

#define LEAF_LENGTH 32

char* side(int index);

int get_parent_index(int index);
int get_sibling_index(int index);

uint8_t* get_leaves(Tree* tree, int branch);
uint8_t* hash_siblings(const uint8_t* left, const uint8_t* right);

void update_parent(Tree* tree, int branch_index, int leaf_index, _Bool recurse);
void rebuild_branch(Tree* tree, int branch_index, int start_index, int end_index);

void replace(uint8_t* leaves, const uint8_t* leaf, int size, int index);
void delete(uint8_t* leaves, int size, int index);

const uint8_t empty[LEAF_LENGTH] = { 0 };

enum status {SUCCESS = 0, INDEX_ERROR = 1, EMPTY = 2};

void add_branch(Tree* tree) {
    Branch branch;

    branch.leaves = malloc(LEAF_LENGTH * 2);
    memcpy(branch.leaves, tree->root, LEAF_LENGTH);
    memcpy(branch.leaves + LEAF_LENGTH, empty, LEAF_LENGTH);
    memcpy(tree->root, empty, LEAF_LENGTH);
    branch.leaf_count = 2;
    
    tree->branches = realloc(tree->branches, (tree->branch_count + 1) * sizeof(Branch));
    tree->branches[tree->branch_count] = branch;
    tree->branch_count++;
}

void expand_branch(Branch* branch) {
    branch->leaves = realloc(branch->leaves, branch->leaf_count * 2 * LEAF_LENGTH);
    for (int i = branch->leaf_count * LEAF_LENGTH; i < branch->leaf_count * 2 * LEAF_LENGTH; i += 32) {
        memcpy(branch->leaves + i, empty, LEAF_LENGTH);
    }
    branch->leaf_count += branch->leaf_count;
}

void remove_branch(Tree* tree) {
    memcpy(tree->root, tree->branches[tree->branch_count - 1].leaves, LEAF_LENGTH);
    tree->branches = realloc(tree->branches, (tree->branch_count - 1) * sizeof(Branch));
    tree->branch_count--;
}

void prune_branch(Branch* branch) {
    branch->leaves = realloc(branch->leaves, branch->leaf_count / 2 * LEAF_LENGTH);
    branch->leaf_count = branch->leaf_count / 2;
}

uint8_t* hash(uint8_t* in, int len) {
    static uint8_t hash[LEAF_LENGTH];
    SHA256(in, len, hash);

    return hash;
}

uint8_t* hash_siblings(const uint8_t* left, const uint8_t* right) {
    uint8_t* in = malloc(2 * LEAF_LENGTH);
    memcpy(in, left, LEAF_LENGTH);
    memcpy(in + LEAF_LENGTH, right, LEAF_LENGTH);

    return hash(in, LEAF_LENGTH * 2);
}

/* create and return a new tree */
Tree* new_tree(unsigned char* leaves[], int count) {
    Tree* tree = malloc(sizeof(Tree));

    tree->root = malloc(32);
    memcpy(tree->root, empty, 32);

    tree->branches = malloc(0);

    tree->branch_count = 0;
    tree->leaf_count = 0;

    for (int i = 0; i < count; i++) {
        add_leaf(tree, leaves[i], LEAF_LENGTH, 1);    
    }

    return tree;
}

unsigned char* get_root(Tree *tree) {
    return tree->root;
}

void update_parent(Tree* tree, int branch_index, int leaf_index, _Bool recurse) {
    uint8_t leaf[LEAF_LENGTH];
    uint8_t sibling[LEAF_LENGTH];
    memcpy(leaf, tree->branches[branch_index].leaves + leaf_index * LEAF_LENGTH, LEAF_LENGTH);
    int sibling_index = get_sibling_index(leaf_index);
    memcpy(sibling, tree->branches[branch_index].leaves + sibling_index * LEAF_LENGTH, LEAF_LENGTH);

    uint8_t* hash;
    if (strcmp(side(leaf_index), "L") == 0) {
        hash = hash_siblings(leaf, sibling);
    } else {
        hash = hash_siblings(sibling, leaf);
    }

    if (branch_index + 1 == tree->branch_count) {
        memcpy(tree->root, hash, LEAF_LENGTH);
    } else {
        int parent_index = get_parent_index(leaf_index);
        replace(tree->branches[branch_index + 1].leaves, hash, tree->branches[branch_index + 1].leaf_count, parent_index);
        if (recurse) {
            update_parent(tree, branch_index + 1, parent_index, 1);
        }
    }
}

void rebuild_branch(Tree* tree, int branch_index, int start_index, int end_index) {
    if (end_index + 1 < tree->branches[branch_index].leaf_count) {
        replace(tree->branches[branch_index].leaves, empty, tree->branches[branch_index].leaf_count, end_index + 1);
    }
    start_index = strcmp(side(start_index), "L") == 0 ? start_index : start_index - 1;
    end_index = strcmp(side(end_index), "L") == 0 ? end_index + 1: end_index;

    for (int i = start_index; i < end_index; i += 2) {
        update_parent(tree, branch_index, i, 0);
    }
    
    start_index = get_parent_index(start_index);
    end_index = get_parent_index(end_index);

    if (branch_index + 1 < tree->branch_count) {
        rebuild_branch(tree, branch_index + 1, start_index, end_index);
    }
}

void add_leaf(Tree* tree, uint8_t* leaf, int len, _Bool hashed) {
    if (!hashed) {
        leaf = hash(leaf, len);
    }

    if (tree->branch_count == 0 || tree->leaf_count + 1 > tree->branches[0].leaf_count) {
        for (int i = 0; i < tree->branch_count; i++) {
            expand_branch(&tree->branches[i]);
        }
        add_branch(tree);
    }

    int index = tree->leaf_count;

    replace(tree->branches[0].leaves, leaf, tree->branches[0].leaf_count, tree->leaf_count);

    tree->leaf_count++;

    update_parent(tree, 0, index, 1);
}

int update_leaf(Tree *tree, uint8_t *leaf, int index, int len, _Bool hashed) {
    if (index >= tree->leaf_count || index < 0) {
        if (index < 0) {
            return EMPTY;
        }
        return INDEX_ERROR;
    }

    if (!hashed) {
        leaf = hash(leaf, len);
    }

    replace(tree->branches[0].leaves, leaf, tree->branches[0].leaf_count, index);

    update_parent(tree, 0, index, 1);

    return SUCCESS;
}

int remove_leaf(Tree *tree, int index) {
    if (index >= tree->leaf_count || index < 0) {
        if (index < 0) {
            return EMPTY;
        }
        return INDEX_ERROR;
    }

    delete(tree->branches[0].leaves, tree->branches[0].leaf_count, index);

    tree->leaf_count--;

    if (tree->leaf_count == 0) {
        remove_branch(tree);
        memcpy(tree->root, empty, LEAF_LENGTH);
    } else if (tree->leaf_count > 1 && tree->leaf_count <= tree->branches[0].leaf_count / 2) {
        for (int i = 0; i < tree->branch_count; i++) {
            prune_branch(&tree->branches[i]);
        }
        remove_branch(tree);
    }

    if (tree->branch_count > 0) {
        index = index == tree->branches[0].leaf_count ? index - 1 : index;

        rebuild_branch(tree, 0, index, tree->leaf_count - 1);
    }

    return SUCCESS;
}

int get_sibling_index(int index) {
    return strcmp(side(index), "L") == 0 ? index + 1 : index - 1;
}

int get_parent_index(int index) {
    return index / 2;
}

char* side(int index) {
    return (index % 2 == 0) ? "L" : "R";
}

void replace(uint8_t* leaves, const uint8_t* leaf, int size, int index) {
    uint8_t* result = malloc(size * LEAF_LENGTH);
    // in real code you would check for errors in malloc here
    memcpy(result, leaves, size * LEAF_LENGTH);
    memcpy(result + index * LEAF_LENGTH, leaf, 1 * LEAF_LENGTH);
    memcpy(leaves, result, size * LEAF_LENGTH);
    free(result);
}

void delete(uint8_t *leaves, int size, int index) {
    uint8_t* result = malloc((size) * LEAF_LENGTH);
    // in real code you would check for errors in malloc here
    memcpy(result, leaves, index * LEAF_LENGTH);
    memcpy(result + index * LEAF_LENGTH, leaves + (index + 1) * LEAF_LENGTH, (size - index - 1) * LEAF_LENGTH);
    memcpy(result + (size - 1) * LEAF_LENGTH, empty, LEAF_LENGTH);
    memcpy(leaves, result, size * LEAF_LENGTH);
    free(result);
}

int compare(Tree* tree, Tree* other) {
    int result;
    // Two empty trees match...
    if (tree->branch_count == 0 && other->branch_count == 0) {
        return 0;
    }

    result = memcmp(tree->root, other->root, LEAF_LENGTH);

    // Roots don't match
    if (result != 0) {
        return 1;
    }

    // Some how root match but with different leaves.
    if (tree->leaf_count != other->leaf_count) {
        return 1;
    }

    // Some how root matches with different leaves.
    result = memcmp(tree->branches[0].leaves, other->branches[0].leaves, tree->leaf_count * LEAF_LENGTH);
    if (result != 0) {
        return 1;
    }

    return 0;
}
/* unsigned char* get_leaves(Tree *tree, int branch) { */
/*     return tree->branches[branch].leaves; */
/* } */
/*  */
/* void print_leaf(uint8_t* leaf) { */
/*     for (int i=0; i<LEAF_LENGTH; i++) { */
/*         printf("%d", leaf[i]); */
/*     } */
/* } */
/*  */
/* void render(Tree *tree) { */
/*     printf("\nRoot: "); */
/*     unsigned char *root = get_root(tree); */
/*     print_leaf(root); */
/*  */
/*     printf("\nLeaf Count: %d", tree->leaf_count); */
/*     for (int i=0; i<tree->branch_count; i++) { */
/*         printf("\nBranch %d: ", i); */
/*         for (int j=0; j<tree->branches[i].leaf_count * LEAF_LENGTH; j++) { */
/*             printf("%d", tree->branches[i].leaves[j]); */
/*         } */
/*     } */
/* } */
/*  */
/*  */
/* int main() { */
/*     unsigned char* leaves[0]; */
/*     Tree *tree = new_tree(leaves, 0); */
/*     Tree *other = new_tree(leaves, 0); */
/*  */
/*     unsigned char* leaf = (unsigned char *) "a"; */
/*     add_leaf(tree, leaf, 1, 0); */
/*      */
/*     int result = compare(tree, other); */
/*     printf("%d", result); */
/*     return 0; */
/* } */
/*  */
/*     unsigned char* leaf = (unsigned char *) "a"; */
/*     uint8_t* h = hash(leaf, 1); */
/*     for (int i=0; i<LEAF_LENGTH; i++) { */
/*         printf("%d", h[i]); */
/*     } */
/*     add_leaf(tree, leaf, 1, 0); */
/*     render(tree); */
/*  */
/*     remove_leaf(tree, 0); */
/*     render(tree); */
/*     #<{(| leaf = (unsigned char*) "b"; |)}># */
/*     #<{(| add_leaf(tree, leaf, 1, 0); |)}># */
/*     #<{(| render(tree); |)}># */
/*     #<{(| #<{(|  |)}># |)}># */
/*     #<{(| #<{(| leaf = (unsigned char*) "c"; |)}># |)}># */
/*     #<{(| #<{(| update_leaf(tree, leaf, 1, 1, 0); |)}># |)}># */
/*     #<{(| #<{(| render(tree); |)}># |)}># */
/*     #<{(|  |)}># */
/*     #<{(| leaf = (unsigned char*) "c"; |)}># */
/*     #<{(| add_leaf(tree, leaf, 1, 0); |)}># */
/*     #<{(| render(tree); |)}># */
/*     #<{(|  |)}># */
/*     #<{(| leaf = (unsigned char*) "d"; |)}># */
/*     #<{(| add_leaf(tree, leaf, 1, 0); |)}># */
/*     #<{(| render(tree); |)}># */
/*     #<{(|  |)}># */
/*     #<{(| leaf = (unsigned char*) "e"; |)}># */
/*     #<{(| add_leaf(tree, leaf, 1, 0); |)}># */
/*     #<{(| render(tree); |)}># */
/*     #<{(|  |)}># */
/*     #<{(| leaf = (unsigned char*) "f"; |)}># */
/*     #<{(| add_leaf(tree, leaf, 1, 0); |)}># */
/*     #<{(| render(tree); |)}># */
/*     #<{(|  |)}># */
/*     #<{(| #<{(| leaf = (unsigned char*) "cccccccccccccccccccccccccccccccc"; |)}># |)}># */
/*     #<{(| #<{(| update_leaf(tree, leaf, 1); |)}># |)}># */
/*     #<{(| #<{(| render(tree); |)}># |)}># */
/*     #<{(| #<{(|  |)}># |)}># */
/*     #<{(| #<{(| leaf = (unsigned char*) "dddddddddddddddddddddddddddddddd"; |)}># |)}># */
/*     #<{(| #<{(| update_leaf(tree, leaf, 0); |)}># |)}># */
/*     #<{(| #<{(| render(tree); |)}># |)}># */
/*     #<{(| #<{(|  |)}># |)}># */
/*     #<{(| #<{(| leaf = (unsigned char*) "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"; |)}># |)}># */
/*     #<{(| #<{(| update_leaf(tree, leaf, 0); |)}># |)}># */
/*     #<{(| #<{(| render(tree); |)}># |)}># */
/*     #<{(| #<{(|  |)}># |)}># */
/*     #<{(| remove_leaf(tree, 4); |)}># */
/*     #<{(| render(tree); |)}># */
/*     #<{(|  |)}># */
/*     #<{(| remove_leaf(tree, 4); |)}># */
/*     #<{(| render(tree); |)}># */
/*     #<{(| #<{(|  |)}># |)}># */
/*     #<{(| #<{(| leaf = (unsigned char*) "e"; |)}># |)}># */
/*     #<{(| #<{(| add_leaf(tree, leaf, 1, 0); |)}># |)}># */
/*     #<{(| #<{(| render(tree); |)}># |)}># */
/*  */
/*     return 0; */
/* } */
