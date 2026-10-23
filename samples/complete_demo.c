int add(int a, int b) {
    int result = a + b;
    return result;
}
int main() {
    int x = 4;
    int y = 5;
    int total;
    total = add(x, y) + 2 * 3;
    for (int i = 0; i < 3; i++) { total = total + i; }
    return 0;
}
