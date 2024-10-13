import re
from unidecode import unidecode

subjects_enum = [
    ('Toan'),
    ('Van', 'Nguvan', 'Tiengviet'),
    ('Vatly', 'ly'),
    ('Hoahoc', 'Hoa'),
    # ('biology', 'sinhhoc', 'sinh'),
    # ('english', 'tienganh', 'anhvan'),
    # ('history','lichsu', 'su'),
    # ('geography', 'dialy', 'dia'),
    # ('economy','kinhte'),
    # ('computer_science', 'khoahocmaytinh', 'kh', 'khoahoc'),
    # ('other', 'Khác', 'khac', 'other', 'misc')
]

# Tạo pattern_subject bao gồm tất cả các giá trị trong mỗi mục
pattern_subject2 = r'(' + '|'.join(
    '|'.join(unidecode(value.strip().replace(' ', '')).lower() for value in subject)
    for subject in subjects_enum
) + ')'