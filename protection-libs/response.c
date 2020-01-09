#include <stdio.h>
#include <stdlib.h>
#include <execinfo.h>
#include <math.h>

__attribute__((always_inline))
void assert(long long* hash, long long expected) {
  if(*hash != expected){
    exit(1);
  }
}

__attribute__((always_inline))
void oh_hash1(long long *hashVariable, long long value) {
	*hashVariable = *hashVariable + value;
}
__attribute__((always_inline))
void oh_hash2(long long *hashVariable, long long value) {
	*hashVariable = *hashVariable ^ value;
}
