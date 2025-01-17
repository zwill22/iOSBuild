#include "library.h"

#include <stdio.h>

int exampleFunction(struct example * obj) {
    int a = obj->a;
    int b = obj->b;
    char c = obj->c;

    switch (c) {
    case '+':
        return a + b;
    case '-':
        return a - b;
    case 'x':
        return a * b;
    case '/':
        return a / b;
    default:
        printf("Invalid character: %c", c);
        return 0;
    }
}
