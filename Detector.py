import json


class Detector:
    def __init__(self, json_file):
        json_data = open(json_file)
        self.detections = json.load(json_data)

    def get_detections_per_specified_frame(self, frame_num):
        return self.detections[str(frame_num)]

