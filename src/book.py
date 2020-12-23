from dbConnect import connection, cursor

def new_book(book_id, book_name, date_added, book_category):
    sql = '''insert into book(book_id,book_name,date_added,book_category)
                values(?,?,?,?)'''
    
    try:
        output = cursor.execute(sql,[book_id,book_name,date_added,book_category])
        if output:
            connection.commit()
        return True
    except:
        return False
    
def blacklist(book_id,reason):
    sql = """
    --sql
    insert into blacklisted_book(book_id) values(?,?)
    ;
    """
    try:
        cursor.execute(sql, [book_id,reason])
        connection.commit()
        return True
    except:
        return False

def unblacklist(book_id):
    sql = """
    --sql
    delete from blacklisted_books where book_id = ?
    ;
    """
    
    try:
        cursor.execute(sql,[book_id])
        connection.commit()
        return True
    except:
        return False
def book_update(book_id,book_name, date_added, book_category):
    sql = '''update book set book_name = ?, date_added = ?, book_category = ? where book_id = ?'''

    output = cursor.execute(sql, [book_name,date_added, book_category,book_id])
    if output:
        connection.commit()
        return True
    else:
        return False
    
def all_books():
    sql = '''select book_id,book_name,book_category, date_added from book'''
    book_list = cursor.execute(sql).fetchall()
    return book_list
