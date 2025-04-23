#include <stdio.h>
#include <stdlib.h>

int main() {
    int result = system("python D:\\Dev\\Scripts\\shell.py");
    if (result != 0) {
        fprintf(stderr, "Failed\n");
        return 1;
    }
    return 0;
}