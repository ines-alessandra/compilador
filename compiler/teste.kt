val x : Int = 0;
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