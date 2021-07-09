
class Bucket:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def is_empty(self):
        return len(self.items) == 0

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
        return start_index_for_item(self, item)

    def add_item(self, session):
        first_bucket_number = self.start_index_for_item(session)
        last_bucket_number = self.end_index_for_item(session)
        for bucket_number in range(first_bucket_number,
                                 last_bucket_number+1):
            self.buckets[bucket_number].add_item(session)

    def get_buckets(self):
        return self.buckets
    
