from dbConnect import connection, cursor

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
        print('hello world')
        if check_previous_borrow(lib_no,book_no):
            sql = '''insert into book_borrow(lib_no, book_id, date_borrowed, return_date,is_active)
                    values(?,?,?,?,1)'''
            success = cursor.execute(sql, [lib_no,book_no,date_borrowed,return_date])
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
    print(lib_no,' ',book_no)
    success = cursor.execute(sql,[lib_no,book_no])
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
        new_borrow_list.append([borrow[0],borrow[1].capitalize()+' '+borrow[2].capitalize()+' '+borrow[3].capitalize(),borrow[4],borrow[5],borrow[6]])
    
    return new_borrow_list