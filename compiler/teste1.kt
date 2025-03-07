val a : Int = 10;
val b : Bool = true;
print(a);

b = false;

if (a > 15) {
    print(true);
} else {
    print(false);
}

while (a != 0) {
    print(a);
    a = a - 1;
    break;
}

fun multiply(x: Int, y: Int) : Int {
    return x * y;
}

val result : Int = multiply(5, 4);
print(result);

fun calculate() : Int {
    val sum : Int = 10 + 20;
    return sum;
}

fun calculate2() : Int {
    val sum : Int = 10 + 20;
    return sum;
}

val res : Int = calculate();
print(res);

fun greet(name: Int, times: Int, teste: Bool) : Int {
    val i : Int = 0;
    while (i < times) {

        fun a () {
            print(2);
        }

        print(i);
        i = i + 1;
        val a : Int = 10;
        val b : Int = 20;
        while (a < 15) {
            break;
            print(a);
            a = a + 1;
            if (a == 15) {
                print(15);
                continu  e;
            } else {
                print(b);
                continue;
            }
            while (b > 0) {
                print(b);
                continue;
                b = b - 1;
            }
        }
    }
    return 10;
}

greet(1, 3, false);