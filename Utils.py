def remove_item_from_list(listbox, item):
    row = listbox.row(item)
    listbox.takeItem(row)

def format_detections_to_print_out(detections: list):
    return [format_detection_to_print_out(detection) for detection in detections]

def format_detection_to_print_out(detection: list):
    return f'{detection[0]} ({",".join(str(int(num)) for num in detection[1])})'

def extract_detection_data(detection: list):
    return detection[0], format_bounding_box_tuple_to_str(detection[1])


def format_bounding_box_tuple_to_str(bounding_box: tuple):
    return f'({",".join(str(int(num)) for num in bounding_box)})'

def get_index_by_value(lst: list, value):
    # get index from list by value even if value doesn't exist in it (previously add it in this case)
    index = None
    try:
        index = lst.index(value)
    except ValueError:
        lst.append(value)
        index = len(lst) - 1

    return index


def generate_yolo_style_object_detection_row(index, box, frame_width, frame_height):
    center_x, center_y = [box[i] + box[i + 2] / 2 for i in range(2)]
    norm_center_x, norm_center_y = center_x / frame_width, center_y / frame_height
    norm_width, norm_height = box[2] / frame_width, box[3] / frame_height
    label_txt_row = ' '.join(
        [str(value) for value in [index, norm_center_x, norm_center_y, norm_width, norm_height]])
    return f'{label_txt_row}\n'
