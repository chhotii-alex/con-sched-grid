
class Bucket:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def is_empty(self):
        return len(self.items) == 0

    def __len__(self):
        return len(self.items)

    def __getitem__(self, key):
        return self.items[key]

    def get_items(self):
        return self.items

    def contains_same_contents(self, other_bucket):
        if len(self) != len(other_bucket):
            return False
        for i in range(len(self)):
            if self[i] != other_bucket[i]:
                return False
        return True

class BucketArray:
    def __init__(self):
        self.buckets = []
        for bucket in self.make_buckets():
            self.buckets.append(bucket)

    def make_buckets(self):
        raise Exception("Abstract; must override make_buckets")

    def start_index_for_item(self, item):
        raise Exception("Abstract; must override start_index_for_item")

    def end_index_for_item(self, item):
        return self.start_index_for_item(item)

    def add_item(self, session):
        first_bucket_number = self.start_index_for_item(session)
        last_bucket_number = self.end_index_for_item(session)
        for bucket_number in range(first_bucket_number,
                                 last_bucket_number+1):
            self.buckets[bucket_number].add_item(session)

    def get_buckets(self):
        return self.buckets
    
