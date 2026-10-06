# 冒泡排序算法实现

def bubble_sort(arr):
    """
    冒泡排序算法
    时间复杂度: O(n²)
    空间复杂度: O(1)
    """
    # 创建数组副本，避免修改原数组
    sorted_arr = arr.copy()
    n = len(sorted_arr)
    
    # 外层循环控制排序轮数
    for i in range(n):
        # 标记本轮是否发生交换，用于优化
        swapped = False
        
        # 内层循环进行相邻元素比较和交换
        # 每轮后最大元素会"冒泡"到末尾，所以范围逐渐缩小
        for j in range(0, n - i - 1):
            if sorted_arr[j] > sorted_arr[j + 1]:
                # 交换元素
                sorted_arr[j], sorted_arr[j + 1] = sorted_arr[j + 1], sorted_arr[j]
                swapped = True
        
        # 如果本轮没有发生交换，说明数组已经有序，可以提前结束
        if not swapped:
            break
    
    return sorted_arr


def bubble_sort_inplace(arr):
    """
    原地冒泡排序（直接修改原数组）
    """
    n = len(arr)
    
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break


# 测试代码
if __name__ == "__main__":
    # 测试用例
    test_arrays = [
        [64, 34, 25, 12, 22, 11, 90],
        [5, 2, 8, 1, 9],
        [1],
        [],
        [3, 3, 3, 3],
        [5, 4, 3, 2, 1]
    ]
    
    print("冒泡排序算法测试：")
    print("=" * 50)
    
    for i, arr in enumerate(test_arrays, 1):
        print(f"测试 {i}: {arr}")
        original = arr.copy()
        result = bubble_sort(arr)
        print(f"排序后: {result}")
        print(f"原数组: {original}")
        print()
    
    # 测试原地排序
    print("原地排序测试：")
    test_arr = [64, 34, 25, 12, 22, 11, 90]
    print(f"原数组: {test_arr}")
    bubble_sort_inplace(test_arr)
    print(f"原地排序后: {test_arr}")