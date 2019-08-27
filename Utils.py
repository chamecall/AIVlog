def remove_item_from_list(listbox, item):
    row = listbox.row(item)
    listbox.takeItem(row)