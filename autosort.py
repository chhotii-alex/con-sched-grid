#!/usr/bin/env python3

import math
import random

class AutoSortedArray:
    def __init__(self):
        self.array = []

    def __str__(self):
        return str(self.array)

    def append(self, item):
        i = self.index_of_successor(item)
        self.array = self.array[:i] + [item] + self.array[i:]
       
    def __contains__(self, item):
        i = self.index_of(item)
        return i is not None
 
    def index_of_successor(self, item):
        if not len(self.array):
            return 0
        return self.index_of_successor_in_range(item, 0, len(self.array)-1)

    def index_of_successor_in_range(self, item, low_end, high_end):
        if low_end == high_end:
            if item == self.array[low_end]:
                raise Exception("Attempt to add duplicate item")
            if item < self.array[low_end]:
                return low_end
            else:
                return  low_end+1
        mid = math.floor((low_end+high_end)/2)
        if item <= self.array[mid]:
            return self.index_of_successor_in_range(item, low_end, mid)
        else:
            return self.index_of_successor_in_range(item, mid+1, high_end)

    def index_of(self, item):
        return self.index_of_in_range(item, 0, len(self.array)-1)

    def index_of_in_range(self, item, low_end, high_end):
        if low_end > high_end:
            return None
        if self.array[high_end] == item:
            return high_end
        if low_end == high_end:
            return None
        mid = math.floor((low_end+high_end)/2)
        if self.array[mid] >= item:
            return self.index_of_in_range(item, low_end, mid)
        else:
            return self.index_of_in_range(item, mid+1, high_end)

    def __len__(self):
        return len(self.array)
    
    def __getitem__(self, key):
        return self.array[key]

def run_unit_tests():
    a = AutoSortedArray()
    a.append(3)
    try:
        a.append(3)
        exception_raised = False
    except:
        exception_raised = True
    if not exception_raised:
        raise Exception("Should've raised exeption on duplicate 3")
    if not 3 in a:
        raise Exception("Couldn't find 3 in a")
    if 5 in a:
        raise Exception("Hey, I didn't add 5 to a")
    for _ in range(250):
        r = random.randint(-250, 250)
        if r not in a:
            a.append(r)
    print(a)
    for i in range(1, len(a)):
        if a[i-1] > a[i]:
            raise Exception("Yo, didn't work!")
    if 27 not in a:
        a.append(27)
    try:
        a.append(27)
        exception_raised = False
    except:
        exception_raised = True
    if not exception_raised:
        raise Exception("Should've raised exeption on duplicate 27")

    a = AutoSortedArray()
    a.append("banana")
    a.append("date")
    a.append("cherry")
    a.append("apple")
    print(a)
    for i in range(1, len(a)):
        if a[i-1] > a[i]:
            raise Exception("Yo, didn't work!")

if __name__ == "__main__":
    run_unit_tests()

