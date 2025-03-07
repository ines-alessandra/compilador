val x : Int = 10;
x = 1000;
const y : Int = x;
fun foo() : Int {
    const a : Int = 40;
    return a;
}
val a : Int = foo();
while (x < 10) {
    x = x + 1;
    if (x == 5) {
        const g : Int = x;
        break;
    } else {
        const g : Int = 10;
        continue;
    }
}
fun baz(i : Int, j : Int)  {
    val z : Int = i;
    if (z < 40) {
        z = z + i + j;
    } else {
        const teste : Bool = true;
        z = z - i - j;
    }
    print(z);
}

baz(10, 20);