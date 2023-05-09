from bezbot.tgbot import config
import sqlite3
import telebot

bot = telebot.TeleBot(config.token)

db = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = db.cursor()

def raznost(kls):
    for val in cursor.execute("SELECT * from amount"):
        if kls == val[0]:
            raznost = val[1] - val[2]
            return raznost

def update_children_data(id, tx):
    tx = tx.split()
    kls = tx[0]
    kls = kls.upper()
    kol = int(tx[1])
    kab = tx[2]
    for val in cursor.execute("SELECT * FROM teachers"):
        tg_id = val[0]
        if tg_id == id:
            cursor.execute("Update teachers set klass = ? where tg_id = ?", (kls, id))
            cursor.execute("Update amount set amount = ? where class = ?", (kol, kls))
            cursor.execute("Update teachers set cabinet = ? where tg_id = ?", (kab, id))
            db.commit()
            return kls

def text_data_substitution(tx1, tx2, tx3, tx4, tx5, tx6, tx7, tx8):
    txt1 = tx1 + ' - ' + str(tx2) + ' человек(а), ' + tx3 + ' кабинет' + '\n => Недосчитано: '+ str(tx5) + ' человек(а) \n--- Было: '+ str(tx4) + ' человек(а)' + ' \n--- С детьми: ' + tx6 + ' ' + tx7 + ' ' + tx8
    return txt1


def output_info_klass(id):
    global kkls, amount, kab, before, rznst, n, sn, p
    cursor.execute("SELECT * from teachers")
    for val in cursor.execute("SELECT * from teachers"):
        if val[0] == id:
            n = val[1]
            sn = val[2]
            p = val[3]
            kkls = val[5]
            kab = val[6]
    for vl in cursor.execute("SELECT * from amount"):
        if vl[0] == kkls:
            before = vl[1]
            amount = vl[2]
            rznst = before - amount
    db.commit()
    text = text_data_substitution(kkls, amount, kab, before, rznst, n, sn, p)
    return text

def output_info_class(id):
    global  cls, kls, amount, kab, before, rznst, n, sn, p
    for vaal in cursor.execute("SELECT * from teachers"):
        if vaal[0] == id:
            cls = vaal[4]
    for val in cursor.execute("SELECT * from teachers"):
        if val[5] == cls:
            n = val[1]
            sn = val[2]
            p = val[3]
            kab = val[6]
    for vl in cursor.execute("SELECT * from amount"):
        if cls == vl[0]:
            before = vl[1]
            amount = vl[2]
            rznst = before - amount
    db.commit()
    text = text_data_substitution(cls, amount, kab, before, rznst, n, sn, p)
    text = 'Ваш класс:\n' + text
    return text

def total_count():
    before = 0
    amount = 0
    for p in cursor.execute("SELECT * from amount"):
        before += p[1]
        amount += p[2]
        db.commit()
    rznst = before - amount
    text = 'Статистика на данный момент:\n---Общее количество: ' + str(before) + '\n---В безопасности: ' + str(amount) + '\n---Недостающие: ' + str(rznst)
    return text

@bot.message_handler(commands=['start'])
def start(message):
    n = message.from_user.first_name
    sn = message.from_user.last_name
    print(message.chat.id, ': ', n, sn)
    try:
        for val in cursor.execute("SELECT * from teachers"):
            if val[0] == message.chat.id:
                mess = f'Здравствуйте, <b>{message.from_user.first_name} {message.from_user.last_name}</b>'
                bot.send_message(message.chat.id, mess +'!\nПожалуйста, напишите важную информацию.', parse_mode='html')
    except:
        bot.send_message(message.chat.id, f'Обратитесь к админу. Вас нет в базе данных!')


@bot.message_handler(commands=['terror'])
def teror(message):
    for val in cursor.execute("SELECT * from teachers"):
        id = val[0]
        bot.send_message(id, 'Запущен протокол мероприятия по антитеррористической защите!!!')
        bot.send_message(id, 'Напишите КЛАСС,\nКОЛИЧЕСТВО детей и КАБИНЕТ, в котором вы забарикадировались, !!!ЧЕРЕЗ ПРОБЕЛ!!!')
        bot.send_message(id, 'Пример:\n\n"1а  27  101"\n\n"1а" - класс, \n"27" - количество детей,\n"101" - номер кабинета!')
    db.commit()

@bot.message_handler(commands=['evacuation'])
def evacuation(message):
    for val in cursor.execute("SELECT * from teachers"):
        id = val[0]
        bot.send_message(id, 'Запущен протокол мероприятия по Эвакуации!!!')
        bot.send_message(id, 'Напишите КЛАСС,\nКОЛИЧЕСТВО детей и КАБИНЕТ, который вы покинули, !!!ЧЕРЕЗ ПРОБЕЛ!!!')
        bot.send_message(id, 'Пример:\n\n"1а  27  101"\n\n"1а" - класс, \n"27" - количество детей,\n"101" - номер кабинета!')
    db.commit()

@bot.message_handler(commands=['startposition'])
def start_position(presence):
    global none
    none = ''
    try:
        cursor.execute("Update students set presence = 0")
        cursor.execute("Update amount set amount = 0")
        cursor.execute("Update amount set before = 0")
        db.commit()
        bot.send_message(presence.chat.id, f'Начальная позиция установлена успешно')
    except:
        print("Ошибка при работе с SQLite")

@bot.message_handler(commands=['help'])
def start(message):
    bot.send_message(message.chat.id, config.help_users)

@bot.message_handler(commands=['helpadmin'])
def start(message):
    bot.send_message(message.chat.id, config.help_admin)

@bot.message_handler(commands=["inform"])
def mes(message):
    bot.send_message(message.chat.id, 'Напишите КЛАСС, КОЛИЧЕСТВО детей и КАБИНЕТ, !!!ЧЕРЕЗ ПРОБЕЛ!!!')
    bot.send_message(message.chat.id, 'Пример:\n\n"1а  27  101"\n\n"1а" - класс, \n"27" - количество детей,\n"101" - номер кабинета!')

@bot.message_handler(commands=['infoall'])
def mes(message):
    # global dl, kkls
    # lst = []
    # cursor.execute("SELECT * from teachers")
    # for val in cursor.execute("SELECT * from teachers"):
    #     k = val[5]
    #     if k != 'None':
    #         lv = [val[3], ' - ', val[4], 'человек, ', 'Эвакуировал(а): ', val[1], val[2]]
    #         lv = str(lv)
    #         lv = lv.replace("[", "")
    #         lv = lv.replace("]", "")
    #         lv = lv.replace(",", "")
    #         lv = lv.replace("'", "")
    #         bot.send_message(message.chat.id, lv)
    # try:
    # for poz in cursor.execute("SELECT * from teachers"):
    #     idid = [poz[0]]
    #     lst.append(idid)
    # db.commit()
    # print(lst, len(lst))
    # for x in lst:
    #     text = output_info_klass(x)
    #     print(text)


        # bot.send_message(message.chat.id, str(text))
    #except:
        #print('Ошибка вывода данных о всех классах')
    try:
        text = total_count()
        bot.send_message(message.chat.id, text)
    except:
        print('Ошибка вывода общего количества')

@bot.message_handler(commands=['info'])
def website(message):
    id = message.from_user.id
    try:
        info_klass = output_info_klass(id)
        bot.send_message(message.chat.id, str(info_klass))
    except:
        print('Ошибка вывода данных 1!')
    try:
        info_class = output_info_class(id)
        bot.send_message(message.chat.id, str(info_class))
    except:
        print('Ошибка вывода данных 2!')

@bot.message_handler(content_types=['text'])
def mes(message):
    text = message.text
    id = message.from_user.id
    try:
        klass = update_children_data(id, text)
        bot.send_message(id, 'Данные обновлены!')
        rznst = raznost(klass)
        bot.send_message(id, 'Недосчитано: ' + str(rznst) + 'человек(а)')
        bot.send_message(message.chat.id, '\nНажмите на команду /info , чтобы уточнить информацию')
        info_class = output_info_class(id)
        bot.send_message(message.chat.id, str(info_class))
    except:
        bot.send_message(id, 'Данного класса не существует!')
        print('Вводят несуществующий класс')
    try:
        info_klass = output_info_klass(id)
        bot.send_message(config.admin, str(info_klass))
        print(str(info_klass))
        print('-----PERFECT-----')
    except:
        print('Ошибка отправки сообщения админу!!!')
        pass


bot.polling(none_stop=True)