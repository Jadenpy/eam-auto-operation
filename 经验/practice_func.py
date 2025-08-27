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