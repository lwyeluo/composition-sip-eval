#include <stdint.h>
#include <stdio.h>
#include <execinfo.h>
#include <stdlib.h>
__attribute__((always_inline))
void guardMe(const unsigned int address) {
  
  const unsigned char *beginAddress = (const unsigned char *) address;
  const unsigned char length = (const unsigned char) address;
  const unsigned char expectedHash = (const unsigned char) address;
  unsigned int visited = 0;
  unsigned char hash = 0;
  while (visited < length) {
    hash ^= *beginAddress++;
    ++visited;
  }

  if (hash != expectedHash) {
    exit(1);
  }
}

/*__attribute__((always_inline))
void guardMe(const unsigned int address, const unsigned int length, const unsigned int expectedHash) {

  const unsigned char *beginAddress = (const unsigned char *) address;
  unsigned int visited = 0;
  unsigned char hash = 0;
  while (visited < length) {
    hash ^= *beginAddress++;
    ++visited;
  }

  if (hash != (unsigned char) expectedHash) {
    exit(1);
  }
}*/

