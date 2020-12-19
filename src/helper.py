from book import all_books
from lib_user import all_staff,all_students

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

def list_to_string(old_list,index):
    new_list = []
    for book in old_list:
        new_list.append(book[index])

    return new_list