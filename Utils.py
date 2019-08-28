def remove_item_from_list(listbox, item):
    row = listbox.row(item)
    listbox.takeItem(row)

def format_detections_to_print_out(detections: list):
    return [f'{i+1} ({detection[0]})' for i, detection in enumerate(detections)]