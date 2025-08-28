# 函数的信息了解
# help(print)

def calculate(a, b=10, operation = '+'):
    if operation == '+':
        return a+b
    elif operation == '-':
        return a-b
    elif operation == '*':
        return a*b
    elif operation == '/':
        if b != 0:
            return a/b
        print(f'b不能等于0！')
    else:
        return None
    
# print(calculate(5))  # 5 + 10 = 15
# print(calculate(8, 3, "*"))  # 8 * 3 = 24
# print(calculate(10, 2, "/"))  # 10 / 2 = 5.0
# print(calculate(5, 3, "^"))  # None（不支持^）


# lambda的联系
def add(*args):
    sum = 0
    
    for _ in args:
        sum += _

    return sum

# print(add(1,2,3,4))
# print(add(*(1,2,3)))


# f = lambda a : a+1

# print((type(f)))

# print(f(2))

# numbers = [1, -3, 5, -2, 4]

# zhengshu = list(filter(lambda x: x>0, numbers))

# sqare_all = list(map(lambda x: x*x, numbers))

# evens =  list(filter(lambda x : x % 2 ==0,numbers))

# print(zhengshu)
# print(sqare_all)
# print(evens)


import time

def timer(func):
    def wrapper(*args , **kwargs):
        start = time.time()  # 开始
        result = func(*args, **kwargs)
        end = time.time()
        print(f'用时约{(end - start) * 1000 :.2f}毫秒')
        return result
    return wrapper


@timer
def my_sleep():
    time.sleep(1)



my_sleep()