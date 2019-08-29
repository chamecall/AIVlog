def remove_item_from_list(listbox, item):
    row = listbox.row(item)
    listbox.takeItem(row)

def format_detections_to_print_out(detections: list):
    return [format_detection_to_print_out(detection) for detection in detections]

def format_detection_to_print_out(detection: list):
    return f'{detection[0]} ({",".join(str(int(num)) for num in detection[2])})'

def extract_detection_data(detection: list):
    return detection[0], f'({",".join(str(int(num)) for num in detection[2])})'