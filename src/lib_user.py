from dbConnect import cursor, connection

def add_lib_user(fname, sname,other_name, user_type , **kwargs):
    if user_type == 'STUDENT':
        std_class = kwargs['std_class']
        stream = kwargs['stream']
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

        success_insert = cursor.execute(sql, [lib_no, fname, sname, other_name,std_class, stream])

        
    else:
        phone_no = kwargs['phone_no']
        sql = ''' insert into lib_user(lib_no, first_name, second_name, other_name,user_type, phone_number)
                    values(?,?,?,?,'STAFF',?)'''

        gen_sql = '''select lib_no from lib_user where user_type = 'STAFF' order by lib_no desc limit 1'''
        latest = cursor.execute(gen_sql).fetchone()

        if latest:
            lib_no = 'STF' + prefixer(str(int(latest[0].split(latest[0][2])[1]) + 1))
        else:
            lib_no = 'STF001'

        success_insert = cursor.execute(sql, [lib_no, fname, sname, other_name,phone_no])

    if success_insert:
        connection.commit()
        return True
    else:
        return False

def all_students():
    students = cursor.execute('select lib_no, first_name,second_name,other_name,class,stream from lib_user where user_type = "STUDENT"').fetchall()

    new_student_list = []
    for student in students:
        new_student_list.append([student[0],student[1].capitalize() + ' '+ student[2].capitalize()+' ' + student[3].capitalize(), str(student[4])+' '+student[5].capitalize()])
    return new_student_list

def all_staff():
    staff = cursor.execute('select lib_no, first_name, second_name, other_name, phone_number from lib_user where user_type = "STAFF" ').fetchall()

    new_staff_list = []
    for each_staff in staff:
        new_staff_list.append([each_staff[0], each_staff[1] + ' ' + each_staff[2].capitalize() + ' ' +each_staff[3].capitalize(),each_staff[4]])

    return new_staff_list

def prefixer(string):
    if len(string) == 1:
        return '00'+string
    elif len(string) == 2:
        return '0'+string
    else:
        return string