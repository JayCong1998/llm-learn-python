def test():
    test1()
    print("12345")
# test()  在此处调用,会报错,因为test1()未定义
def test1():
    test2()
    print("9999")
def test2():
    test3()
    print("88888")
def test3():
    print("77777")
test()