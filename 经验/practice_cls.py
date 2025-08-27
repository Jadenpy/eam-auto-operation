# 1. 基础类定义与实例化
class Person():
    def __init__(self,name,age):
        self.name = name
        self.age = age
    def introduce(self):
        print(f'我叫{self.name}，今年{self.age}岁')

# p1 = Person('张三',43)
# p2 = Person('李四',21)
# p1.introduce()
# p2.introduce()

# 2. 类属性与实例属性
# class Student():
#     school = '阳光小学'
#     def __init__(self,name,grade):
#         self.name = name
#         self.grade = grade
#     def get_info(self):
#         print(f'{self.name}在{self.school}{self.grade}年级')

# s1 = Student('张三','一')
# s2 = Student('李四','二')
# s3 = Student('王五','三')
# s1.get_info()
# s2.get_info()
# s3.get_info()

# 3. 私有属性与访问控制
# 题目：定义一个 BankAccount 类，包含私有属性 __balance（余额，初始为 0），以及方法 deposit(amount)（存款）、withdraw(amount)（取款，需判断余额是否充足）、get_balance()（返回当前余额）。禁止直接修改 __balance，验证私有属性的访问限制。

class BankAccount():
    
    def __init__(self,balance = 0):
        self.__balance = balance
    def deposit(self,amount):
        if amount <= 0:
            print('存款金额必须大于0')
        else:
            self.__balance  += amount
            print(f'存款成功，当前余额为{self.__balance}')
    def withdraw(self,amount):
        # check amount if gt __balance
        if amount > self.__balance:
            print('余额不足')
        else:
            self.__balance -= amount
            print(f'取款成功，当前余额为{self.__balance}')
        
    def get_balance(self):
        return self.__balance
    
# a1 = BankAccount(1000)
# a1.deposit(1000)
# a1.withdraw(2000)
# print(a1.get_balance())
# # __私有属性：不能通过实例直接访问
# # print(a1.__balance)


# 4. 继承与方法重写
# 题目：基于第 1 题的 Person 类，定义子类 Teacher，新增属性 subject（教的科目），并重写 introduce() 方法，打印 “我叫 XX，教 XX”。再定义子类 Student（继承 Person），新增属性 grade，重写 introduce() 为 “我叫 XX，读 X 年级”。创建两个子类实例并调用 introduce()。
class Teacher(Person):
    def __init__(self, name, age, subject):
        super().__init__(name, age)
        self.subject = subject
    
    def introduce(self):
        print(f'我叫{self.name}，教{self.subject}')


class Student(Person):
    def __init__(self, name, age, grade):
        super().__init__(name, age)
        self.grade = grade

    def introduce(self):
        print(f'我叫{self.name}，读{self.grade}年级')


# t1 = Teacher('张三', 30, '数学')
# t1.introduce()
# s1 = Student('李四', 15, 3)
# s1.introduce()

# 5. 多继承与 super() 用法
# 题目：定义类 A（方法 foo() 打印 “来自 A”）、类 B（方法 foo() 打印 “来自 B”），再定义类 C 同时继承 A 和 B，并在 C 的 bar() 方法中分别调用 A 和 B 的 foo() 方法（使用 super() 或类名）。观察多继承中方法调用的顺序。
class A():
    def foo(self):
        print('来自 A')


class B():
    def foo(self):
        print('来自 B')


class C(B, A):
    def bar(self):
        super().foo()
        A.foo(self)


# c1 = C()
# c1.bar()

# 6. 类装饰器应用

# 7. 魔术方法实践
class Book():
    def __init__(self,title,price):
        self.title = title
        self.price = price

    def __str__(self):
        return f'《{self.title}》价格：{self.price}元'
    
    def __repr__(self):
        return f"Book(title='{self.title}', price={self.price})"
    
    def __add__(self,other):
        return self.price + other.price
    
# [Book("Python", 59), Book("Java", 69), Book("C++", 49)]
# print(Book("Python", 59)+Book("Java", 69))
# b1 = Book("Python", 59) 
# b2 = Book("Java", 69)   
# print(b1)
# print(repr(b1))
# total = b1 + b2
# print(total)
#怎么调用 __repr__     __add__的定义与使用
# 8. 抽象基类（ABC）
import abc
class Shape(abc.ABC):
    @abc.abstractmethod
    def area(self):
        pass

    @abc.abstractmethod
    def perimeter(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius * self.radius

    def perimeter(self):
        return 2 * 3.14 * self.radius
    
class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)
    
# Shape 抽象基类不能被实例化
# s = Shape()  # 报错，Shape 是抽象基类，不能被实例化
# Shape 的子类 Circle 和 Rectangle 必须实现 area 和 perimeter 方法
# c = Circle(5)
# print(c.area())  # 输出 78.5
# print(c.perimeter())  # 输出 31.400000000000002

# r = Rectangle(4, 6)
# print(r.area())  # 输出 24
# print(r.perimeter())  # 输出 20

# 类的元编程（动态添加方法）
# 9.类的元编程（动态添加方法）
# 题目：定义一个空类 DynamicClass，通过 types.MethodType 动态为其添加一个实例方法 greet(self, name)（打印 “Hello, XX”），再添加一个类方法 info(cls)（打印 “这是动态类”）。创建实例并调用新增的方法。
import types
class DynamicClass():
    pass
# 方法定义
def greet(self, name):
    print(f"Hello, {name}")

def info(cls):
    print(f"这是动态类{cls.__name__}的info方法")
# 绑定到DynamicClass
DynamicClass.greet = types.MethodType(greet, DynamicClass)
DynamicClass.info = types.MethodType(info, DynamicClass)

# d1 = DynamicClass()
# d1.greet("Jaden")  # 输出 Hello, Alice
# d1.info()
# DynamicClass.info()

# TODO: 上下文管理器（__enter__/__exit__）
# 10. 上下文管理器（__enter__/__exit__）
# 题目：定义一个 FileHandler 类，实现上下文管理器接口，用于自动打开和关闭文件。使用 with FileHandler("test.txt", "w") as f: 时，自动打开文件，在 with 块中可写入内容，退出块时自动关闭文件（即使发生异常）。验证文件是否正确关闭。
class FileHandler():
    pass




# 综合练习

class Student():
    def __init__(self, id, name, scores:dict):
        self.id = id
        self.name = name
        self.scores = scores

    def get_average(self):
        """
                计算平均分
        :return: 平均分数
        """
        # 计算self.scores 中所有值的和，再除以self.scores 的长度
        total = sum(self.scores.values())
        count = len(self.scores)
        avg = total / count
        return round(avg, 2)
        
       


class StudentManager():
    def __init__(self, students:list):
        self.students = students

    def add_student(self, student:Student):
        """
                添加学生
        :param: student
        :return: students
        """
        print(f"添加前有{len(self.students)}个学生")
        self.students.append(student)
        print('添加成功')
        print(f"添加后有{len(self.students)}个学生")
        # return self.students

    def remove_student(self,id):
        """
                根据id删除学生
        :param: id
        :return: students
        """
        # 查找，打印学生信息
        f_stu = self.find_student(id)
        if f_stu:
            print(f'删除前，有{len(self.students)}个学生')
            # 二次确认是否删除            
            if input('确定删除吗？(y/n):') == 'y':
                self.students.remove(f_stu)
                print(f'学号为{id}的学生已删除！')
                print(f'删除后，有{len(self.students)}个学生')
                # 返回删除后的学生列表
                # return self.students
            else:
                print(f'删除动作取消，未删除任何学生信息！')
                # return self.students
        else:
            # 提示未找到
            print(f'抱歉，未找到学号{id}的学生')
        
        

    def find_student(self,id):
        """
                根据id查找学生
        :param: id
        :return: student
        """
        for student in self.students:
            if student.id == id:
                return student
        print(f'抱歉，未找到学号{id}的学生')
        return None

    def get_top_student(self):
        """
                获取平均分最高的学生
        :return: student 
        
        """
        return max(self.students,key=lambda x:x.get_average())
    
    def get_students(self):
        """
                获取所有学生
        :return: list
        """
        return self.students


# s1 = Student('001','张三',{"语文": 92, "数学": 88, "英语": 95, "物理": 89})
# s2 = Student('002','李四',{"语文": 88, "数学": 92, "英语": 89, "物理": 25})
# s3 = Student('003','王五',{"语文": 95, "数学": 89, "英语": 92, "物理": 88})
# s4 = Student('004','赵六',{"语文": 89, "数学": 75, "英语": 88, "物理": 92})
# s5 = Student('005','钱七',{"语文": 92, "数学": 89, "英语": 95, "物理": 98})


# students = [s1, s2, s3, s4, s5]

# # 创建一个学生管理器对象
# manager = StudentManager(students)

# # print(s1.get_average())
# # print(s2.get_average())
# # print(s3.get_average())
# # print(s4.get_average())
# # print(s5.get_average())

# # f_s = manager.find_student('005')
# # if f_s:
# #     print(f_s.name)

# # top_s = manager.get_top_student()
# # print(top_s.name)
# s6 = Student('006','小明',{"语文": 92, "数学": 88, "英语": 95})
# manager.add_student(s6)
# # print(manager.get_students())
# manager.remove_student('006')



