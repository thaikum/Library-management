from .dbConnect import connection, cursor


def check_previous_borrow(lib_no, book_no):
    sql = """
    --sql
    SELECT lib_no from book_borrow where lib_no = ? and book_id = ? and is_active = 1
    ;
    """
    active = cursor.execute(sql, [lib_no, book_no]).fetchone()
    if active:
        return False
    else:
        return True


def is_blacklisted(book_id):
    sql = """
    --sql
    SELECT book_id from blacklisted_books where book_id = ?
    ;
    """
    blacklisted = cursor.execute(sql, [book_id]).fetchone()
    if blacklisted:
        return True
    else:
        return False


def new_borrow(lib_no, book_no, date_borrowed, return_date):
    if not is_blacklisted(book_no):
        if check_previous_borrow(lib_no, book_no):
            sql = '''insert into book_borrow(lib_no, book_id, date_borrowed, return_date,is_active)
                    values(?,?,?,?,1)'''
            success = cursor.execute(sql, [lib_no, book_no, date_borrowed, return_date])
            if success:
                connection.commit()
                return True

            return False
        else:
            return "active"
    else:
        return "blacklisted"


def return_book(lib_no, book_no):
    sql = ''' update book_borrow set is_active = 0 where lib_no = ? and book_id = ? and is_active = 1'''
    success = cursor.execute(sql, [lib_no, book_no])
    if success:
        connection.commit()
        return True
    else:
        return False


def all_borrows():
    sql = '''select bb.lib_no, lb.first_name, lb.second_name, lb.other_name, bb.book_id, bb.date_borrowed, bb.return_date 
            from book_borrow bb
            join lib_user lb on lb.lib_no = bb.lib_no
            where bb.is_active = 1'''

    borrow_list = cursor.execute(sql).fetchall()
    new_borrow_list = []
    for borrow in borrow_list:
        new_borrow_list.append(
            [borrow[0], borrow[1].capitalize() + ' ' + borrow[2].capitalize() + ' ' + borrow[3].capitalize(), borrow[4],
             borrow[5], borrow[6]])

    return new_borrow_list


def range_selection(start_date, end_date):
    sql = """SELECT b.book_name, b.book_category, b.form_class, count(b.book_name) as `total` from book_borrow bb left join book b on b.book_id = bb.book_id where bb.date_borrowed between ? and ? group by b.book_name, b.form_class, b.book_category
    """

    result = cursor.execute(sql, [start_date, end_date]).fetchall()
    return result


def range_selection_by_date(book_name, book_category, form_class, start_date, end_date):
    sql = """SELECT bb.date_borrowed, count(b.book_name) as `total` 
            from book_borrow bb 
            left join book b on b.book_id = bb.book_id 
            where b.book_name = ? and b.book_category = ?and b.form_class = ? and bb.date_borrowed between ? and ? group by b.book_name, b.form_class, b.book_category, bb.date_borrowed
    """

    result = cursor.execute(sql, [book_name, book_category, form_class, start_date, end_date]).fetchall()
    return result


def borrowing_history():
    sql = '''select bb.lib_no, lb.first_name, lb.second_name, lb.other_name, bb.book_id, bb.date_borrowed, bb.return_date 
            from book_borrow bb
            join lib_user lb on lb.lib_no = bb.lib_no'''

    borrow_list = cursor.execute(sql).fetchall()
    new_borrow_list = []
    for borrow in borrow_list:
        new_borrow_list.append(
            [borrow[0], borrow[1].capitalize() + ' ' + borrow[2].capitalize() + ' ' + borrow[3].capitalize(), borrow[4],
             borrow[5], borrow[6]])

    return new_borrow_list


def history():
    sql = '''select bb.lib_no, l.first_name || ' ' || l.second_name || ' ' || other_name as student_name, 
            bb.book_id, b.book_name, strftime('%d-%m-%Y',bb.date_borrowed), strftime('%d-%m-%Y',bb.return_date)
            from book_borrow bb
            join lib_user l on bb.lib_no = l.lib_no
            join book b on bb.book_id = b.book_id'''
    try:
        hist = cursor.execute(sql).fetchall()
        return True, hist
    except Exception as e:
        return False, e
