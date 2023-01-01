# Написать программу, выполняющую операции (сложение и вычитание) с простыми дробями.
# Дроби вводятся и выводятся в формате: n x/y
# ,где n - целая часть, x - числитель, у - знаменатель.
# Дроби могут быть отрицательные и не иметь целой части, или иметь только целую часть.

# Примеры:
# Ввод: 5/6 + 4/7 (всё выражение вводится целиком в виде строки)
# Вывод: 1 17/42  (результат обязательно упростить и выделить целую часть)
# Ввод: -2/3 - -2
# Вывод: 1 1/3

fract = '5/6 + 4/7 -2/3 - -2'  #input(' Введите выражение с дробями в формате: n x/y')
print(fract)
fract = fract.replace('- -', '+')
split_plus = fract.split('+')

terms = []
for term in split_plus:
    if len(term.split('-')) > 1:
        split_minus = term.split('-')
        if split_minus.count(' ') == 0 and split_minus.count('') == 0:
            terms.append(split_minus[0])
            for i in range(1, len(split_minus)):
                terms.append('-' + split_minus[i])
        if split_minus.count('') != 0:
            terms.append('-' + split_minus[1])
    else:
        terms.append(term)

def convert_fract(f):
    if f.count('-') != 0:
        k = -1
        f = f.replace('-', '')
    else:
        k = 1

    f = f.strip().split(' ')
    if len(f) == 2:
        n = int(f[0])
        x = int(f[1].split('/')[0])
        y = int(f[1].split('/')[1])

        denum = y
        numer = k * (n*y + x)
    elif f[0].find('/') != -1:
        denum = int(f[0].split('/')[1])
        numer = k * int(f[0].split('/')[0])
    else:
        denum = 1
        numer = k * int(f[0])
    return (numer, denum)

def sum_fract(f1, f2):
    numer = f1[0]*f2[1] + f2[0]*f1[1]
    denum = f1[1]*f2[1]

    delim = hcf(numer, denum)
    numer /= delim
    denum /= delim
    return (int(numer), int(denum))

def hcf(x, y): # selecting the smaller number
    x = abs(x)
    y = abs(y)
    if x > y:
        smaller = y
    else:
        smaller = x

    if smaller != 0:
        for i in range(1, smaller + 1):
            if ((x % i == 0) and(y % i == 0)):
                hcf = i
    else:
        hcf = 1
    return hcf

def simplyfer(f):
    """
    выделяет целую часть из дроби f = x/y
    :param f:
    :return: n x y
    """
    if f[0] < 0:
        sigx = -1
    else:
        sigx = 1

    n = int(abs(f[0]) // f[1])
    x = abs(f[0]) - n*f[1]
    y = f[1]

    if n == 0 and x != 0:
        return (sigx*x, y)
    elif n != 0 and x == 0:
        return (n)
    else:
        return (sigx*n, x, y)

def printer(f):
    if f[0] != 0 and f[1] != 0:
        out_fract = str(f[0]) + ' ' + str(f[1]) + '/' + str(f[2])
    elif f[0] == 0 and f[1] != 0:
        out_fract = str(f[1]) + '/' + str(f[2])
    else:
        out_fract = '0'

    print(out_fract)

fracts = []
summa = (0, 1)
for (num, term) in enumerate(terms):
    fracts.append(convert_fract(term))
    summa = sum_fract(summa, fracts[num])

summa = simplyfer(summa)
printer(summa)
