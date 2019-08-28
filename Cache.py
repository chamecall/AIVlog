
class Cache:
    def __init__(self):
        self.all_detections = {}
        self.unused_detections = {}
        self.labels = []
        self.assignments = {}