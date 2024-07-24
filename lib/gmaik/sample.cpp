#include <iostream>
#include <cstring>
using namespace std;

class sample {
private:
    char *p;

public:
    sample(const char *s);
    ~sample();
    sample(const sample &obj);
};

sample::sample(const char *s) {
    int len = strlen(s);
    p = new char[len + 1];
    strcpy(p, s);
}

sample::~sample() {
    delete[] p;
}

sample::sample(const sample &obj) {
    int len = strlen(obj.p);
    p = new char[len + 1];
    strcpy(p, obj.p);
}

int main() {
    const char *str = "Amrita";  // Use a const char* for the string literal
    sample A(str);
    sample B = A;
    return 0;
}

