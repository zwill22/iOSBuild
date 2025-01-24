#ifndef IOS_BUILD_EXAMPLE_PROJECT_HEADER
#define IOS_BUILD_EXAMPLE_PROJECT_HEADER

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

struct example {
    int a;
    int b;
    char c;
};

int exampleFunction(struct example * example_obj);


#ifdef __cplusplus
}
#endif // __cplusplus
#endif // IOS_BUILD_EXAMPLE_PROJECT_HEADER
