import re
from datetime import datetime as dt

from .book import all_books
from .lib_user import all_staff, all_students


def search_book(book_id):
    books = all_books()
    if book_id:
        for book in books:
            if book_id == book[0]:
                return book

    return False


def search_lib_user(lib_id):
    students = all_students()
    staffs = all_staff()
    if lib_id:
        if lib_id[0] == 'S':
            for staff in staffs:
                if staff[0] == lib_id:
                    return staff
        elif lib_id[0] == 'P':
            for student in students:
                if student[0] == lib_id:
                    return student

    return False


def list_to_string(old_list, index):
    new_list = []
    for book in old_list:
        new_list.append(book[index])

    return new_list


def search(list_to_search, search_id):
    new_list = []
    search_re = re.compile(search_id, re.I)

    for item in list_to_search:
        for ind in item:
            if search_re.match(ind):
                new_list.append(item)
                break

    return new_list


def get_date_list(old_list, date_index):
    new_list = []
    for item in old_list:
        new_list.append(dt.strptime(item[date_index], '%Y-%m-%d'))

    return new_list


def get_total(old_list, index):
    total = 0
    for item in old_list:
        total += int(item[index])

    return str(total)


def one_to_two_lists(old_list):
    list_index_0 = []
    list_index_1 = []
    for item in old_list:
        list_index_0.append(dt.strptime(item[0], '%Y-%m-%d'))
        list_index_1.append(dt.date((item[1])))
    return [list_index_0, list_index_1]
