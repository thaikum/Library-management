from dbConnect import connection, cursor

def check_previous_borrow(lib_no):
    pass

def new_borrow(lib_no, book_no, date_borrowed, return_date):
    sql = '''insert into book_borrow(lib_no, book_id, date_borrowed, return_date,is_active)
            values(?,?,?,?,1)'''
    success = cursor.execute(sql, [lib_no,book_no,date_borrowed,return_date])
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