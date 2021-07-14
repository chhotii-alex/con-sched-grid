''' Support class for BucketArray. Instances of this class
or a subclass of this class should be used to contain the 
items that have been sorted by BucketArray.
Quacks like a List, but with some enhancements; and flexible
regarding exactly what the container actually is.
'''
class Bucket:
    def __init__(self, container=None):
        if container is None:
            container = []
        self.items = container

    def add_item(self, item):
        self.items.append(item)

    def is_empty(self):
        return len(self.items) == 0

    def __len__(self):
        return len(self.items)

    def __getitem__(self, key):
        return self.items[key]

    def contains_same_contents(self, other_bucket):
        if len(self) != len(other_bucket):
            return False
        for i in range(len(self)):
            if self[i] != other_bucket[i]:
                return False
        return True

'''
Abstract class for encapsulating the bucket sorting algorithm.
Override: 
* make_buckets() to supply an appropriate number of bucket objects
* index_range_for_item() to supply the first and last bucket's 
    indices that a given object belongs in
This does an O(n) sort, but of limited granularity if more than one
item lands in the same bucket.
'''
class BucketArray:
    def __init__(self):
        self.buckets = []
        for bucket in self.make_buckets():
            self.buckets.append(bucket)

    def make_buckets(self):
        raise Exception("Abstract; must override make_buckets")

    def index_range_for_item(self, item):
        raise Exception("Abstract; must override index_range_for_item")

    def add_item(self, session):
        ''' Sorts one item into the approprate bucket(s). '''
        first_bucket_number, last_bucket_number  = \
            self.index_range_for_item(session)
        for bucket_number in range(first_bucket_number,
                                 last_bucket_number+1):
            self.buckets[bucket_number].add_item(session)

    def get_buckets(self):
        return self.buckets
    
