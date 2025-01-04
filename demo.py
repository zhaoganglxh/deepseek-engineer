def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[-1]
    left = [x for x in arr[:-1] if x <= pivot]
    right = [x for x in arr[:-1] if x > pivot]
    return quicksort(left) + [pivot] + quicksort(right)


def test_quicksort():
    # Test case 1: Unsorted array
    arr = [10, 7, 8, 9, 1, 5]
    expected = [1, 5, 7, 8, 9, 10]
    assert quicksort(arr) == expected, 'Test case 1 failed'
    
    # Test case 2: Already sorted array
    arr = [1, 2, 3, 4, 5]
    expected = [1, 2, 3, 4, 5]
    assert quicksort(arr) == expected, 'Test case 2 failed'
    
    # Test case 3: Single element array
    arr = [42]
    expected = [42]
    assert quicksort(arr) == expected, 'Test case 3 failed'
    
    # Test case 4: Empty array
    arr = []
    expected = []
    assert quicksort(arr) == expected, 'Test case 4 failed'
    
    print('All test cases passed!')

# Run the test
if __name__ == '__main__':
    test_quicksort()