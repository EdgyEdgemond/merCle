// merkle.h
typedef struct {
    int leaf_count;
    unsigned char* leaves;
} Branch;

typedef struct {
    uint8_t* root;
    int branch_count;
    int leaf_count;
    Branch* branches;
} Tree;

Tree* new_tree(unsigned char* leaves[], int count);
uint8_t* get_root(Tree* tree);
void add_leaf(Tree *tree, uint8_t* leaf, int len, _Bool hashed);
int update_leaf(Tree *tree, uint8_t* leaf, int index, int len, _Bool hashed);
int remove_leaf(Tree *tree, int index);
int compare(Tree* tree, Tree* other);
