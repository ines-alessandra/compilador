val x : Int = 10;
x = 1000;
val y : Int = x;

fun foo(i: Int, j : Int) : Int {
    const a : Int = 40;
    return a;
}

const c : Int = 10 + foo(1, 2) * 20 + 4 * 2 - 1 + 5 * 10 + 2 + 3 + 3 + 2 * 2 / 1;


val a : Int = foo(1, 2);

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

fun baz(i : Int, j : Int) {
    val z : Int = i;
    if (z < 40) {
        z = z + i + (10 + 1) + j * 10;
    } else {
        val teste : Bool = true;
        z = z - i - j;
    }
    print(z, foo(1, 2), 2);
}

baz(10, 20);
a = foo(foo(foo((1 + foo(1, 2)) + 1, 2), 2), (foo(1, 2) + 1) + 1);
print(a);