from pathlib import Path

import py_tender_cli.make_list as make_list

print("make_list loaded from:")
print(Path(make_list.__file__).resolve())

print()
print("_SUB_ITEM pattern:")
print(make_list._SUB_ITEM.pattern)

print()
print("72(ii) match:")
print(
    make_list._sub_item_parts("(ii) Gypsum False Ceiling/ Calcium Silicate/GRG Ceiling")
)

print()
print("normalize_make_list source:")
print(make_list.normalize_make_list.__code__.co_filename)
