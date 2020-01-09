// Requires openSSL development package. Install with apt-get install libssl-dev
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

#define DEBUG 0

typedef struct node {
	char *value;
	struct node *next;
} node_t;

node_t *stack = NULL;
int stack_len = 0;

int built_matrix = 0;
char **mapping;
char **adj_mat;
int vertices_count;
__attribute__((always_inline))
void registerFunction(char functionName[]) {
	node_t *next = stack;
	while (next != NULL) {
		// if(next->value == functionName) {
		// 	return;
		// }
		next = next->next;
	}

	stack_len++;
	node_t *new_node = (node_t *) malloc(sizeof(node_t));
	new_node->value = functionName;
	new_node->next = stack;
	stack = new_node;
	if (DEBUG) {
		printf("Stack: ");
		next = stack;
		while (next != NULL) {
			printf("%s ; ", next->value);
			next = next->next;
		}
		printf("\n");
	}
}
__attribute__((always_inline))
void deregisterFunction(const char functionName[]) {
	if (stack == NULL) {
		fprintf(stderr, "Error: No function on shadow stack that can be poped!\n");
		return;
	}
	if (stack->value != functionName) {
		return;
	}

	stack_len--;
	node_t *next_node = stack->next;
	free(stack);
	stack = next_node;
	if (DEBUG) {
		node_t *next = stack;
		printf("Stack: ");
		while (next != NULL) {
			printf("%s ; ", next->value);
			next = next->next;
		}
		printf("\n");
	}
}


/**
 * Binary search: O(log(n)), only works for sorted list!
 */
int binarySearch(char ***list, char *str, int len) {
	if (DEBUG) printf("BinarySearch\n");
	int start = 0;
	int end = len;
	int pos;
	while (end >= start) {
		pos = start + ((end - start) / 2);
		if (strcmp((*list)[pos], str) == 0) {
			if (DEBUG) printf("Found\n");
			return pos;
		} else if (start == end) {
			if (DEBUG) printf("Found nothing\n");
			return -1;
		} else if (strcmp((*list)[pos], str) < 0) {
			start = pos + 1;
		} else {
			end = pos;
		}
	}
	if (DEBUG) printf("Found nothing\n");
	return -1;
}

int stringcmp(const void *a, const void *b) {
	const char **ia = (const char **) a;
	const char **ib = (const char **) b;
	return strcmp(*ia, *ib);
}

/*
* Reads known edges from file 'X.txt' line by line.
* Returns pointer to array of known edges and number of edges read.
*/
void readEdges(char ***mapping, char ***adj_mat, int *vertices_count) {
	if (DEBUG) printf("Reading edges...\n");
	FILE *fp;
	size_t len = 12;// getline reallocs (doubles) buffer and len if it's too small
	char *l = (char *) malloc(len * sizeof(char));

	char *toks;

	int next = 0;

	fp = fopen("graph.txt", "r");
	if (fp == NULL) {
		fprintf(stderr, "Failed to read graph file.\n");
		exit(1);
	}

	if (getline(&l, &len, fp) == -1) return;
	*vertices_count = (int) strtol(l, (char **) NULL, 10);

	if (getline(&l, &len, fp) == -1) return;
	int line_count = (int) strtol(l, (char **) NULL, 10);

	// alloc func buffer
	char **buffer = (char **) malloc(2 * line_count * sizeof(char *));
	if (buffer == NULL) {
		fprintf(stderr, "Failed to alloc buffer.\n");
		exit(1);
	}
	if (DEBUG) printf("Allocated buffer\n");

	// Alloc mapping
	*mapping = (char **) malloc(*vertices_count * sizeof(char *));
	if (*mapping == NULL) {
		fprintf(stderr, "Failed to alloc mapping.\n");
		exit(1);
	}
	if (DEBUG) printf("Allocated mapping\n");

	// Alloc adjacency matrix
	*adj_mat = (char **) malloc(*vertices_count * sizeof(char *));
	if (*adj_mat == NULL) {
		fprintf(stderr, "Failed to alloc adjacency matrix.\n");
		exit(1);
	}
	for (int i = 0; i < *vertices_count; i++) {
		(*adj_mat)[i] = (char *) malloc(*vertices_count * sizeof(char));
		if ((*adj_mat)[i] == NULL) {
			fprintf(stderr, "Failed to alloc adj_mat[%d].\n", i);
			exit(1);
		}
	}
	if (DEBUG) printf("Allocated adj_mat\n");

	int count = 0;
	while (getline(&l, &len, fp) != -1) {
		toks = strtok(l, " ");
		toks[strcspn(toks, "\n")] = 0;

		while (toks != NULL) {
			buffer[count] = (char *) malloc(len * sizeof(char));

			strncpy(buffer[count], toks, len);
			count++;
			int found = binarySearch(mapping, toks, next - 1);
			if (found == -1) {
				(*mapping)[next] = (char *) malloc(len * sizeof(char));
				strncpy((*mapping)[next], toks, len);
				next++;
				qsort(*mapping, (size_t) next, sizeof(char *), stringcmp);
			}
			toks = strtok(NULL, " ");
			if (toks != NULL)
				toks[strcspn(toks, "\n")] = 0;
		}
	}

	if (DEBUG) {
		for (int i = 0; i < *vertices_count; i++) {
			printf("List[%d]=%s\n", i, (*mapping)[i]);
		}
	}

	for (int i = 0; i < 2 * line_count; i += 2) {
		int row = binarySearch(mapping, buffer[i], *vertices_count);
		int col = binarySearch(mapping, buffer[i + 1], *vertices_count);
		if (row == -1 || col == -1) {
			if (DEBUG) printf("Unexpected row/col for %s -> %s\n", buffer[i], buffer[i + 1]);
		}
		(*adj_mat)[row][col] = 1;
	}

	free(l);
	for (int i = 0; i < 2 * line_count; i++) {
		free(buffer[i]);
	}
	free(buffer);
}
__attribute__((always_inline))
void responseCFI() {
	exit(1);
}

void verify(char ***mapping, char ***adj_mat, int vertices_count) {
	node_t *curr = stack, *next;
	char *curr_name;
	char *next_name;

	if (curr == NULL || curr->next == NULL) {
		return;
	}
	char *func = stack->value;
	next = curr->next;

	do {
		curr_name = curr->value;
		next_name = next->value;


		int col = binarySearch(mapping, curr_name, vertices_count);
		int row = binarySearch(mapping, next_name, vertices_count);

		if (row == -1) {
			responseCFI();
			return;
		}
		if (col == -1) {
			responseCFI();
			return;
		}
		if ((*adj_mat)[row][col] != 1) {
			responseCFI();
			return;
		}
		curr = next;
		next = curr->next;
	} while (next != NULL);

}
__attribute__((always_inline))
void verifyStack() {
	readEdges(&mapping, &adj_mat, &vertices_count);
        node_t *curr = stack, *next;
        char *curr_name;
        char *next_name;

        char *func = stack->value;
        next = curr->next;
        
        do {    
                curr_name = curr->value;
                next_name = next->value;
                
                
                int col = binarySearch(mapping, curr_name, vertices_count);
                int row = binarySearch(mapping, next_name, vertices_count);
                
                if (adj_mat[row][col] != 1) {
                        responseCFI();
                        return;
                }
                curr = next;
                next = curr->next;
        } while (next != NULL);


}
