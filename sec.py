from telebot import TeleBot
import mysql.connector

from time import sleep


class DirectBot:
    def __init__(self):
        self.bot = TeleBot('815071611:AAH5oTHw-ao0Q35WYHexfwMm-0p0WIvtR_o')
        self.myConnection = mysql.connector.connect(host="127.0.0.1",
                                                    user='root',
                                                    passwd='1111',
                                                    db='sclick_schema')
        self.cursor = self.myConnection.cursor()

    def main_function(self):
        @self.bot.message_handler(content_types=["new_chat_members"])
        def handler_new_member(message):
            self.bot.send_message(message.chat.id, 'Добро пожаловать, {}! Чтобы занять очередь, напишите '
                                                   '"очередь" в чат, здоровья Вам и Вашим близким!'
                                  .format(message.from_user.first_name))

        @self.bot.message_handler(content_types=['text'])
        def send_mess(message):
            self.cursor.execute("select max(level), max(queue) from sclick_schema.queue")
            for level, qu in self.cursor.fetchall():
                self.last = level
                self.que = qu
            if message.text.upper() == 'ОЧЕРЕДЬ':
                def click(conn):
                    mycursor = conn.cursor()
                    sql = "INSERT INTO sclick_schema.queue (id_users, username, level, queue)" \
                          " VALUES (%s, %s, %s, %s) "
                    val = ("{}".format(message.from_user.id),  "{}".format(message.from_user.first_name),
                           "{}".format(self.last + 1), "{}".format(self.que + 1))
                    mycursor.execute(sql, val)
                    self.myConnection.commit()
                    self.cursor.execute("select queue, level from sclick_schema.queue "
                                        "where id_users = {}".format(message.from_user.id))
                    for queue, i in self.cursor.fetchall():
                        self.bot.send_message(message.chat.id, " Добро пожаловать в систему, Ваша очередь = "
                                                               " {} !".format(queue))

                try:
                    click(self.myConnection)
                except Exception:
                    self.cursor.execute("select queue, level from sclick_schema.queue "
                                        "where id_users = {}".format(message.from_user.id))
                    for queue, level in self.cursor.fetchall():
                        self.bot.send_message(message.chat.id, " Ваша очередь = "
                                                               " {} !".format(queue))

            if message.text.upper() == "МИНУС ОЧЕРЕДЬ":
                us = self.bot.get_chat_member(message.chat.id, message.from_user.id)
                if us.status == "administrator" or us.status == "creator":
                    self.cursor.execute("update sclick_schema.queue set queue = queue-1")
                    self.myConnection.commit()
                    self.bot.send_message(message.chat.id, 'очередь сдвинута на 1 пункт')
                else:
                    self.bot.send_message(message.chat.id, 'данная команда вам недоступна')
                    print(us.status)

            if message.text.upper() == 'СПИСОК':
                self.cursor.execute("select username, queue from sclick_schema.queue where queue between 0 and 4 "
                                    "order by queue")
                lst = "Список юзеров в очереди:\n\n"

                for usnm, ue in self.cursor.fetchall():
                    lst += f"{ue}. {usnm}\n"
                self.bot.send_message(message.chat.id, lst)

            if message.text.upper() == 'ПОЛНЫЙ СПИСОК':
                self.cursor.execute("select username, queue from sclick_schema.queue ")
                lst = "Список юзеров в очереди:\n\n"

                for usnm, ue in self.cursor.fetchall():
                    lst += f"{ue}. {usnm}\n"
                self.bot.send_message(message.chat.id, lst)

    def non_stop(self):
        while True:
            try:
                self.bot.polling(none_stop=True)
            except Exception as exepts:
                print(exepts)
                sleep(15)


bt = DirectBot()
bt.main_function(), bt.non_stop(), bt.infa()
