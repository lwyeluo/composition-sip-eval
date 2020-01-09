clang-7 -Wno-everything cfi-funcs.c -c -emit-llvm -o cfilib.bc
clang-7 -Wno-everything response.c -c -emit-llvm -o ohlib.bc
clang-7 -Wno-everything rtlib.c -c -emit-llvm -o sclib.bc
