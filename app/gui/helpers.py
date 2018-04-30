from __future__ import division, print_function


def find_lcm(num1, num2):
    if (num1 > num2):
        num = num1
        den = num2
    else:
        num = num2
        den = num1
    rem = num % den
    while (rem != 0):
        num = den
        den = rem
        rem = num % den
    gcd = den
    lcm = int(int(num1 * num2) / int(gcd))
    return lcm


def global_lcm(numbers):
    if len(numbers) < 2:
        return None
    elif len(numbers) == 2:
        return find_lcm(numbers[0], numbers[1])
    else:
        num1 = numbers[0]
        num2 = numbers[1]
        lcm = find_lcm(num1, num2)

        for i in range(2, len(numbers)):
            lcm = find_lcm(lcm, numbers[i])

        print(lcm)
        return lcm


