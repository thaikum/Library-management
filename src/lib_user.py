from src.dbConnect import cursor, connection


def add_lib_user(fname, sname, other_name, user_type, **kwargs):
    if user_type == 'STUDENT':
        std_class = kwargs['std_class']
        stream = kwargs['stream']
        updating_lib_no = kwargs.get('lib_no')

        if updating_lib_no:
            sql = '''update lib_user set first_name = ?, second_name = ?, other_name = ?, class = ?, stream = ?
                    where lib_no = ?'''
            result = cursor.execute(sql, [fname, sname, other_name, std_class, stream, updating_lib_no])
            if result:
                connection.commit()
                return True
            else:
                return False

        else:
            sql = '''
                insert into lib_user(lib_no,first_name,second_name,user_type, other_name,class,stream)
                values(?,?,?,'STUDENT',?,?,?)
            '''

            gen_sql = '''select lib_no from lib_user where user_type = 'STUDENT' order by lib_no desc limit 1'''
            latest = cursor.execute(gen_sql).fetchone()

            if latest:
                lib_no = 'PP' + prefixer(str(int(latest[0].split(latest[0][1])[2]) + 1))
            else:
                lib_no = 'PP001'

            success_insert = cursor.execute(sql, [lib_no, fname, sname, other_name, std_class, stream])

    else:
        phone_no = kwargs['phone_no']
        lib_no = kwargs['lib_no']
        if lib_no:
            sql = '''update lib_user set first_name = ?, second_name = ?, other_name = ?, phone_number = ?
                    where lib_no = ?'''
            success_insert = cursor.execute(sql, [fname, sname, other_name, phone_no, lib_no])
        else:
            sql = ''' insert into lib_user(lib_no, first_name, second_name, other_name,user_type, phone_number)
                        values(?,?,?,?,'STAFF',?)'''

            gen_sql = '''select lib_no from lib_user where user_type = 'STAFF' order by lib_no desc limit 1'''
            latest = cursor.execute(gen_sql).fetchone()

            if latest:
                lib_no = 'STF' + prefixer(str(int(latest[0].split(latest[0][2])[1]) + 1))
            else:
                lib_no = 'STF001'

            success_insert = cursor.execute(sql, [lib_no, fname, sname, other_name, phone_no])

    if success_insert:
        connection.commit()
        return True
    else:
        return False


def all_students():
    students = cursor.execute(
        'select lib_no, first_name,second_name,other_name,class,stream from lib_user where user_type = "STUDENT"'). \
        fetchall()

    new_student_list = []
    for student in students:
        new_student_list.append(
            [student[0], student[1].capitalize() + ' ' + student[2].capitalize() + ' ' + student[3].capitalize(),
             str(student[4]) + ' ' + student[5].capitalize()])
    return new_student_list


def all_staff(user_type='normal'):
    if user_type == 'super':
        sql = '''select l.lib_no, l.first_name, l.second_name, l.other_name,l.phone_number, a.is_superadmin
                from lib_user l
                left join authentication a on l.lib_no = a.lib_no
                where user_type = 'STAFF' '''
    else:
        sql = 'select lib_no, first_name, second_name, other_name, phone_number from lib_user where user_type = ' \
              '"STAFF" '

    staff = cursor.execute(sql)

    new_staff_list = []
    for each_staff in staff:
        row = [each_staff[0], each_staff[1] + ' ' + each_staff[2].capitalize() + ' ' + each_staff[3].capitalize(),
               each_staff[4]]
        if len(each_staff) == 6:
            if each_staff[5] == 1:
                row.append('Super Admin')
            elif each_staff[5] == 0:
                row.append('Admin')
            else:
                row.append('')

        new_staff_list.append(row)

    return new_staff_list


def prefixer(string):
    if len(string) == 1:
        return '00' + string
    elif len(string) == 2:
        return '0' + string
    else:
        return string


def create_admin(lib_no, password=None):
    if password:
        sql = '''select lib_no from authentication where lib_no = ?'''
        if cursor.execute(sql, [lib_no]).fetchone():
            sql = '''select lib_no from authentication where lib_no =? and password is null'''
            if cursor.execute(sql, [lib_no]).fetchone():
                sql = '''update authentication set password = ? where lib_no = ?'''
                cursor.execute(sql, [password, lib_no])
                connection.commit()
                return True,
            else:
                return False, f'User {lib_no} already exists'
        else:
            return False, 'Sorry you are not authorised to perform this action'
    else:
        sql = """INSERT INTO authentication(lib_no,is_superadmin) values(?,0)"""
        result = cursor.execute(sql, [lib_no])
        connection.commit()
        return result


def login_admin(lib_no, password):
    sql = '''SELECT lib_no from authentication where lib_no = ? and password = ?'''
    result = cursor.execute(sql, [lib_no, password]).fetchone()
    return result


def change_password(lib_no, old_password, new_password):
    sql = '''select lib_no from authentication where lib_no = ? and password = ?'''
    result = cursor.execute(sql, [lib_no, old_password]).fetchone()
    if result:
        sql = '''update authentication set password = ? where lib_no = ?'''
        result = cursor.execute(sql, [new_password, lib_no])
        connection.commit()
        if result:
            return True
        else:
            return False
    else:
        return False


def update_staff(lib_no, first_name, second_name, other_name, phone_no):
    sql = '''update lib_user set first_name = ?, second_name = ?, other_name = ?, phone_number = ?where lib_no = ?'''
    result = cursor.execute(sql, [first_name, second_name, other_name, phone_no, lib_no])
    if result:
        connection.commit()
        return True
    else:
        return False


def get_staff_details(lib_no):
    sql = '''select first_name, second_name, other_name, phone_number from lib_user where lib_no = ?'''
    result = cursor.execute(sql, [lib_no]).fetchone()
    if result:
        return result
    else:
        return False


def get_admin_type(lib_no):
    sql = '''select is_superadmin from authentication where lib_no = ?'''
    result = cursor.execute(sql, [lib_no]).fetchone()
    if result[0]:
        return 'super'
    else:
        return 'normal'


def blacklist_user(lib_no, reason):
    sql = '''insert into blacklisted_user(lib_no, blacklisting_reason) values(?,?)'''
    result = cursor.execute(sql, [lib_no, reason])
    if result:
        connection.commit()
        return True
    else:
        return False


def unblacklist_user(lib_no):
    sql = '''delete from blacklisted_user where lib_no = ?'''
    result = cursor.execute(sql, [lib_no])

    if result:
        connection.commit()
        return True
    else:
        return False


def check_for_user_blacklist(lib_no):
    sql = '''select lib_no from blacklisted_user where lib_no = ?'''
    result = cursor.execute(sql, [lib_no]).fetchone()

    if result:
        return True
    else:
        return False


def de_admin(lib_no):
    sql = '''delete from authentication where lib_no = ?'''
    result = cursor.execute(sql, [lib_no])
    if result:
        connection.commit()
        return True
    else:
        return False


def promote_individal_student(lib_no, action):
    if action == 'promote':
        sql = '''update lib_user set class = class + 1 where lib_no = ?'''
    else:
        sql = '''update lib_user set class = class - 1 where lib_no = ?'''
    result = cursor.execute(sql, [lib_no])
    if result:
        connection.commit()
        return True
    else:
        return False


def promote_all_students(action):
    if action == 'promote':
        sql = '''update lib_user set class = class + 1 where user_type = "STUDENT" '''
    else:
        sql = '''update lib_user set class = class - 1 where user_type = "STUDENT" '''

    result = cursor.execute(sql)
    if result:
        connection.commit()
        return True
    else:
        return False
