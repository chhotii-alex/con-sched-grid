#!/usr/bin/env python3

import math
import random

'''
The AutoSortedArray class encapsulates a list and arranges such that 
if we add items one by one (using the .append() method), we do not have 
to remember to sort the list after populating it-- items are inserted
in sorted order. 
A binary search is done to determine the correct index to insert to
maintain the sort order. Thus, adding n items to a previously empty
collection is O(n*log(n)), just as adding n items and then sorting the list
would be.
'''
class AutoSortedArray:
    def __init__(self):
        self._array = []

    def __str__(self):
        return str(self._array)

    def append(self, item):
        i = self.index_of_successor(item)
        self._array = self._array[:i] + [item] + self._array[i:]
       
    def __contains__(self, item):
        i = self.index_of(item)
        return i is not None
 
    '''
    Find the index at which the given item would have to
    be inserted to maintain my _array's sort order.
    Examples: 
    _array is empty: return 0
    _array = [1, 3, 4], item = 2: return 1
    _array = [1, 3, 4], item = 5: return 3
    Preconditions: 
    * my _array is sorted in ascending order 
    * my _array contains no duplicate items
    * item is comparable to elements already in the _array using the 
       comparison operators
    * item is not equivalent to any element currently in my _array
    Postcondition: either any item in the _array is larger than the given
    item, and the return value is the _array of the smallest such; or
    the return value is the size of the _array.
    '''
    def index_of_successor(self, item):
        ''' Outcome A: either postcondition (return value size of _array) holds
            or we actually have to do a search '''
        if 0 == len(self._array):
            return 0
        ''' Outcome B: either we have the smallest index of an element larger
            than item, or none such exists and we have None '''
        result = self.index_of_successor_in_range(item, 0, len(self._array)-1)
        if result is None:
            ''' Outcome C1: postcondition for no larger items in _array '''
            return len(self._array)
        else:
            ''' Outcome C2: postcondition for when a larger item in _array '''
            return result

    '''
    Recursive support function for the index_of_successor() method.
    Find the first index of an element of my _array that is larger than
    the given item, if any, within the range low_end to high_end inclusive!!!
    Returns None if there is no such element.
    Example:
    _array = [1, 3, 5, 7], low_end = 0, high_end = 3, item = 4; return 2
    Preconditions:
    * All preconditions listed for index_of_successor() apply here.
    * low_end >= high_end
    * low_end and high_end are valid indices with my _array
    Postcondition:
    No element is larger than item, and the return value is None; or
    return value is the index of an element that is larger than item, and
    return value is minimal.
    '''
    def index_of_successor_in_range(self, item, low_end, high_end):
        # Outcome A: solvable immediately: all elements in this space of 
        #   the _array are smaller than item, and return value is None 
        if item > self._array[high_end]:
            return None 
        # Outcome B1: if we are looking at one position in the _array,
        #    either this index satisfies the postcondition on this space,
        #    or a precondition was violated.
        if low_end == high_end:
            if item < self._array[low_end]:
                return low_end
            # Else if item > the one element: ruled out in O.A above
            else:  # 3rd possibility: equals: a violation 
                raise Exception("Attempt to add duplicate item")
        # Outcome B2: if we are looking at more than one position,
        # divide into two spaces.
        mid = math.floor((low_end+high_end)/2)
        # Outcome C1: either first part may contain a qualifying index,
        # and we satisfy postcondition there...
        if item <= self._array[mid]:
            return self.index_of_successor_in_range(item, low_end, mid)
        # Outcome C2: ...or we satisfy postcondition on second part
        return self.index_of_successor_in_range(item, mid+1, high_end)

    '''
    Return the index of the given item in my _array, or None if it's not
    in the _array.
    Examples:
    _array = [1, 2, 3], item = 1; return 0
    _array = [1, 2, 3], item = 0; return None
    Preconditions: 
    * my _array is sorted in ascending order 
    * my _array contains no duplicate items
    * item is comparable to elements already in the _array using the 
       comparison operators    
    Postcondition: my _array at the index given by the return value is
      equivalent to item, or the return value is None. In other words,
      satisfy the postcondition of index_of_in_range() for the entire
      extent of the list.
    '''
    def index_of(self, item):
        return self.index_of_in_range(item, 0, len(self._array)-1)

    '''
    Return the index of the given item in my _array, if it appears between
    indices low_end and high_end (inclusive!) or None if it doesn't appear
    in that range.
    Examples:
    _array = [1, 2, 3], item = 1, low_end = 1; return None
    _array = [1, 2, 3], item = 1, low_end = 0; return 0
    Preconditions: 
    See Preconditions for index_of() method.
    Also:
    * low_end and high_end are valid indices within my _array.
    Postcondition: my _array at the index given by the return value is
      equivalent to item, and low_end <= return value <= high_end
      or the return value is None
    '''
    def index_of_in_range(self, item, low_end, high_end):
        # Outcome A: (solvable immediately?): no elements in range;
        # or, there are elements to be searched
        if low_end > high_end:
            return None
        # Outcome B: (solvable immediately?): 
        # item is found at first index, return this value;
        # or, we have ruled out that item is at first index
        if self._array[low_end] == item:
            return low_end
        # Outcome C: (solvable immedately?):
        # search space consists of one element, & it's not item (see O.B); 
        # or, there's space to be searched, so we divide into two parts
        if low_end == high_end:
            return None
        mid = math.floor((low_end+high_end)/2)
        # Outcome D1: either first part may contain the item,
        # and we satisfy postcondition there...
        if self._array[mid] >= item:
            return self.index_of_in_range(item, low_end+1, mid)
        # Outcome D2: or we satisfy the postcondition on the second part
        return self.index_of_in_range(item, mid+1, high_end)

    def __len__(self):
        return len(self._array)
    
    def __getitem__(self, key):
        return self._array[key]

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

