import pymysql
import uuid
from datetime import datetime
import bcrypt
from flask import Flask, jsonify, request

host = "localhost"
user = "юзер"
password = "пароль"
db_name = "некая бд"


# Подключение к базе - работает
def create_connection_bd(host_name, port_name, user_name, user_password, db_name):
    connect = None
    try:
        connect = pymysql.connect(
            host=host_name,
            port=port_name,
            user=user_name,
            password=user_password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"Error {e}")
    return connect


# Хеширование пароля
def hash_password(user_password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), salt)
    return hashed_password


# Проверка хешированного пароля
def check_password(input_password, hashed_password):
    try:
        test = bcrypt.checkpw(input_password.encode('utf-8'), hashed_password.encode('utf-8'))
        return test
    except Exception as e:
        print(f"Error {e}")
        return False


app = Flask(__name__)


@app.route('/некая ссыль', methods=['POST'])
def update_chat_connect():
    data = request.get_json()
    id_user = data['id_user']
    chats = ''
    a_chats = ''
    try:
        connect = create_connection_bd(host, 3306, user, password, db_name)
        with connect.cursor() as cursor:
            update_chat = "SELECT `id_chat`, name_chat, id_user2 FROM `chat_users` WHERE `id_user1` = %s"
            cursor.execute(update_chat, id_user)
            chats = cursor.fetchall()
            update_chat = "SELECT `id_chat`, name_chat, id_user1 FROM `chat_users` WHERE `id_user2` = %s"
            cursor.execute(update_chat, id_user)
            a_chats = cursor.fetchall()
            if chats == ():
                chats = []
            else:
                for chat in chats:
                    if 'id_user2' in chat:
                        chat['id_user1'] = chat.pop('id_user2')
            if a_chats == ():
                a_chats = []
            else:
                for a_chat in a_chats:
                    if 'id_user2' in a_chat:
                        a_chat['id_user1'] = a_chat.pop('id_user2')
    finally:
        connect.close()
    # TODO: Need correct this bullshit
    all_chats = chats + a_chats
    if len(all_chats) == 0:
        return '404'
    else:
        return all_chats


@app.route('/некая ссыль', methods=['POST'])
def entry_in_chat():
    data = request.get_json()
    id_chat = data['id_chat']
    messages = ''
    try:
        connect = create_connection_bd(host, 3306, user, password, db_name)
        with connect.cursor() as cursor:
            entry = "SELECT * FROM message WHERE id_chat = %s"
            cursor.execute(entry, id_chat)
            messages = cursor.fetchall()
    finally:
        connect.close()
    if len(messages) == 0:
        return '404'
    else:
        return messages


# Работает
@app.route('/некая ссыль', methods=['POST'])
def input_in_system():
    id_user = ''
    search_log = ''
    data = request.get_json()
    log_entry = data['email_user']
    password_entry = data['password_user']
    try:
        connect = create_connection_bd(host, 3306, user, password, db_name)
        with connect.cursor() as cursor:
            log_db = "SELECT `email` FROM `users_chat` WHERE `email` = %s"
            cursor.execute(log_db, log_entry)
            search_log = cursor.fetchone()
    finally:
        connect.close()
    if search_log is None:
        print("email empty")
        return '204'
    else:
        password_db = ''
        try:
            connect = create_connection_bd(host, 3306, user, password, db_name)
            with connect.cursor() as cursor:
                db_output = "SELECT `password` FROM `users_chat` WHERE `email` = %s"
                cursor.execute(db_output, search_log['email'])
                password_db = cursor.fetchone()
        finally:
            connect.close()
        if search_log is not None and check_password(password_entry, password_db['password']):
            status_on = ''
            try:
                connect = create_connection_bd(host, 3306, user, password, db_name)
                with connect.cursor() as cursor:
                    db_output = "SELECT `online` FROM `users_chat` WHERE `email` = %s"
                    cursor.execute(db_output, search_log['email'])
                    status_on = cursor.fetchone()
            finally:
                connect.close()
            print("Okey")
            if status_on['online'] == 0:
                try:
                    connect = create_connection_bd(host, 3306, user, password, db_name)
                    with connect.cursor() as cursor:
                        db_output = "SELECT `id` FROM `users_chat` WHERE `email` = %s"
                        cursor.execute(db_output, search_log['email'])
                        id_user = cursor.fetchone()
                        online_status = "UPDATE `users_chat` SET online=%s WHERE email=%s"
                        values = (1, search_log['email'])
                        cursor.execute(online_status, values)
                    connect.commit()
                finally:
                    connect.close()
                return id_user['id']
            else:
                return '403'
        if len(log_entry) == 0 or len(password_entry) == 0:
            print("zxz")
            return '204'
        else:
            print("not Okey")
            return '401'


# Работает
@app.route('/некая ссыль', methods=['POST'])
def logout_user():
    data = request.get_json()
    id_user = data['id_user']
    try:
        connect = create_connection_bd(host, 3306, user, password, db_name)
        with connect.cursor() as cursor:
            online_status = "UPDATE `users_chat` SET online=%s WHERE id=%s"
            values = (0, id_user)
            cursor.execute(online_status, values)
        connect.commit()
    finally:
        connect.close()
    return '200'


# Работает
@app.route('/некая ссыль', methods=['POST'])
def get_new_chat():
    data = request.get_json()
    id_user = data['id_user']
    searched_user = data['searched_user']
    get_chat_id = uuid.uuid4()
    try:
        connect = create_connection_bd(host, 3306, user, password, db_name)
        with connect.cursor() as cursor:
            update_name_chat = "SELECT email FROM users_chat WHERE id = %s"
            cursor.execute(update_name_chat, id_user)
            user_mail = cursor.fetchone()
            new_noti = ("INSERT INTO `notifications` (id_notification, user_id, about, inv_user_id) "
                        "VALUES (%s, %s, %s, %s)")
            about_noti = f"Пользователь {user_mail['email']} хочет создать с вами чат"
            values = (get_chat_id, searched_user, about_noti, id_user)
            cursor.execute(new_noti, values)
        connect.commit()
    finally:
        connect.close()
    return '200'


# Работает
@app.route('/некая ссыль', methods=['POST'])
def accept_notification():
    data = request.get_json()
    id_notification = data['id_notification']
    accept = data['accept']
    inv_user = ''
    id_user = ''
    get_id = uuid.uuid4()
    try:
        connect = create_connection_bd(host, 3306, user, password, db_name)
        with connect.cursor() as cursor:
            update_noti = "SELECT inv_user_id FROM `notifications` WHERE `id_notification` = %s"
            cursor.execute(update_noti, id_notification)
            inv_user = cursor.fetchone()
            update_noti = "SELECT user_id FROM `notifications` WHERE `id_notification` = %s"
            cursor.execute(update_noti, id_notification)
            id_user = cursor.fetchone()
            del_noti = "DELETE FROM `notifications` WHERE `id_notification` = %s"
            cursor.execute(del_noti, id_notification)
            update_name_chat = "SELECT email FROM users_chat WHERE id = %s"
            cursor.execute(update_name_chat, inv_user['inv_user_id'])
            inv_user_email = cursor.fetchone()
            cursor.execute(update_name_chat, id_user['user_id'])
            id_user_email = cursor.fetchone()
            if accept == 'Yes':
                name_chat = f"Пользователь {inv_user_email['email']} и пользователь {id_user_email['email']}"
                new_chat = "INSERT INTO `chat_users` (id_chat, name_chat, id_user1, id_user2) VALUES (%s, %s, %s, %s)"
                values_user = (get_id, name_chat, inv_user['inv_user_id'], id_user['user_id'])
                cursor.execute(new_chat, values_user)
        connect.commit()
    finally:
        connect.close()
    return '200'


@app.route('/некая ссыль', methods=['POST'])
def notification():
    data = request.get_json()
    id_user = data['id_user']
    notifications = ''
    try:
        connect = create_connection_bd(host, 3306, user, password, db_name)
        with connect.cursor() as cursor:
            update_noti = "SELECT id_notification, about, inv_user_id FROM `notifications` WHERE `user_id` = %s"
            cursor.execute(update_noti, id_user)
            notifications = cursor.fetchall()
    finally:
        connect.close()
    if len(notifications) == 0:
        return '404'
    else:
        return notifications


@app.route('/некая ссыль', methods=['POST'])
def entry_message_db():
    data = request.get_json()
    id_recipient = data['id_recipient']
    id_sender = data['id_sender']
    content_message = data['content_message']
    id_chat = data['id_chat']
    id_message = uuid.uuid4()
    time_message = datetime.now()
    formatted_time = time_message.strftime("%Y-%m-%d %H:%M:%S")
    try:
        connect = create_connection_bd(host, 3306, user, password, db_name)
        with connect.cursor() as cursor:
            new_message = f'''INSERT INTO `message` 
            (id_message, id_recipient, id_sender, time_message, content_message, id_chat) 
                              VALUES (%s, %s, %s, %s, %s, %s)'''
            values_message = (id_message, id_recipient, id_sender, formatted_time, content_message, id_chat)
            cursor.execute(new_message, values_message)
        connect.commit()
    finally:
        connect.close()
    return '200'


# Работает
@app.route('/некая ссыль', methods=['POST'])
def registration_user():
    data = request.get_json()
    email_user = data['email_user']
    password_user = data['password_user']
    search_email = ''
    try:
        connect = create_connection_bd(host, 3306, user, password, db_name)
        with connect.cursor() as cursor:
            check_user = "SELECT email FROM users_chat WHERE email=%s"
            cursor.execute(check_user, email_user)
            search_email = cursor.fetchone()
    finally:
        connect.close()
    password_us = hash_password(password_user)
    id_for_client = ''
    if search_email is None:
        id = 1  # id по умолчанию =1, после идет замена на уникальный
        try:
            connect = create_connection_bd(host, 3306, user, password, db_name)
            with connect.cursor() as cursor:
                new_user = "INSERT INTO `users_chat` (id, email, password, online) VALUES (%s, %s, %s, %s)"
                values_user = (id, email_user, password_us, 0)
                cursor.execute(new_user, values_user)
                new_id = uuid.uuid4()
                query = "UPDATE `users_chat` SET id=%s WHERE id='1'"
                values = str(new_id)
                id_for_client = values
                cursor.execute(query, values)
            connect.commit()
        finally:
            connect.close()
        return {
            'status': '201',
            'id_for_client': id_for_client,
        }
    else:
        print("Пользователь уже зарегистрирован")
        return '400'


# Работает
@app.route('/некая ссыль', methods=['POST'])
def search_user():
    data = request.get_json()
    id_users = data['id_users']
    test_id = ''
    mail = ''
    try:
        connect = create_connection_bd(host, 3306, user, password, db_name)
        with connect.cursor() as cursor:
            search_id = "SELECT id FROM `users_chat` where id=%s"
            cursor.execute(search_id, id_users)
            # тест для функции
            test_id = cursor.fetchone()
            search_email = "SELECT email FROM `users_chat` where id=%s"
            cursor.execute(search_email, id_users)
            mail = cursor.fetchone()
    finally:
        connect.close()
    if test_id is None:
        print("Такого пользователя не существует")
        return '400'
    else:
        print("Пользователь найден")
        return mail['email']


if __name__ == '__main__':
    app.run(host='0.0.0.1', port=5000)
