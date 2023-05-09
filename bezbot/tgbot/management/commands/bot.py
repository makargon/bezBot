from datetime import date, datetime
import telebot
from telebot import types

from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

from tgbot.models import Users, Evacuation, Students, Missing

import tgbot.bot.registration
import tgbot.bot.missing



bot = telebot.TeleBot(settings.BOT_TOKEN)

help_list_start = 'Вам доступны следующие команды:\n' \
                  '/start запустить бота\n' \
                  '/help список доступных команд'
help_list_user = 'Вам доступны следующие команды:\n' \
                 '/start запустить бота\n' \
                 '/absent проверка присутствующих в классе\n' \
                 '/evacuation отправить запрос на общую эвакуацию\n' \
                 '/terror отправить запрос на общую эвакуацию или баррикадирование\n' \
                 '/help список доступных команд'
help_list_admin = 'Вам доступны следующие команды:\n' \
                  '/start запуск бота\n' \
                  '/absent проверка присутствующих в классе\n' \
                  '/evacuation_clear очистка списка эвакуировавшихся или забаррикадированных (введите перед началом эвакуации)\n' \
                  '/evacuation подтверждение начала протокола эвакуации\n' \
                  '/terror подтверждение начала протокола эвакуации или баррикадирования\n' \
                  '/help список доступных команд'


@bot.message_handler(commands=['start'])
def start(message):
    n = message.from_user.first_name
    sn = message.from_user.last_name
    id = message.chat.id
    users = Users.objects.filter(chat_id = id)
    if len(users) == 1 or len(users) == 2:
        user = users[0]
        if user.has_perm('tgbot.evacuate'):
            mess = f'Здравствуйте, <b>{user.last_name} {user.first_name} {user.surename}</b>'
            bot.send_message(id, mess + '!\nВы являетесь администратором!',
                             parse_mode='html')
            bot.send_message(id, help_list_admin)
        else:
            mess = f'Здравствуйте, <b>{user.last_name} {user.first_name} {user.surename}</b>!'
            bot.send_message(id, mess, parse_mode='html')
            bot.send_message(id, help_list_user)
    elif len(users) == 0:
        user = Users()
        user.chat_id = id
        user.username = f'{n} {sn}'
        user.admin_verification = True
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text='Нажмите для начала регистрации', request_contact=True)
        keyboard.add(button_phone)
        sent = bot.send_message(id, "Здравствуйте! Вам необходимо зарегистрироваться.", reply_markup=keyboard)
        bot.register_next_step_handler(sent, tgbot.bot.registration.phone, user=user, bot=bot)
    bot.send_message(908463186, n, sn)
    bot.send_message(839062421, n, sn)
    print(users)
    print(message.chat.id, ': ', n, sn)



@bot.message_handler(commands=['absent'])
def absent(message):
    try:
        user = Users.objects.filter(chat_id=message.chat.id)[0]
        if user.admin_verification:
            tgbot.bot.missing.absent(user=user, bot=bot)
        else:
            bot.send_message(message.chat.id, 'Ваша учётная запись не проверена администратором.')
    except:
        pass


@bot.message_handler(commands=['help'])
def help(message):
    try:
        user = Users.objects.filter(chat_id=message.chat.id)[0]
        if user.admin_verification:
            bot.send_message(message.chat.id, help_list_user)

            if user.has_perm('tgbot.evacuate'):
                bot.send_message(message.chat.id, help_list_admin)

            else:
                bot.send_message(message.chat.id, 'К сожалению у вас нет на это прав')
        else:
            bot.send_message(message.chat.id, 'Ваша учётная запись не проверена администратором.')
    except:
        pass



@bot.message_handler(commands=['absent_edit'])
def absent_edit(message):
    try:
        user = Users.objects.filter(chat_id=message.chat.id)[0]
        if user.admin_verification:
            tgbot.bot.missing.edit_absent(user=user, bot=bot)
        else:
            bot.send_message(message.chat.id, 'Ваша учётная запись не проверена администратором.')
    except:
        pass

@bot.message_handler(commands=['evacuation_clear'])
def evacuation_clear(message):
    user = Users.objects.filter(chat_id=message.chat.id)[0]
    if user.has_perm('tgbot.evacuate'):
        Evacuation.objects.all().delete()
        bot.send_message(message.chat.id, 'База эвакуации очищена!')
    else:
        bot.send_message(message.chat.id, 'К сожалению у вас нет на это прав')



#---------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    try:
        user = Users.objects.filter(chat_id=call.from_user.id)[0]
    except:
        pass
    if call.data == "reg_yes":
        bot.send_message(call.message.chat.id, "Регистрация прошла успешно!")
        bot.send_message(call.message.chat.id, help_list_user)
    elif call.data == "reg_no":
        # user = Users.objects.filter(chat_id=call.from_user.id)[0]
        # try:
        #     usr = Users.objects.get(teacher=user)
        #     usr.delete()
        # except:
        #     pass
        sent = bot.send_message(call.message.chat.id, "Введите верные данные:\nВведите свою фамилию:")
        bot.register_next_step_handler(sent, tgbot.bot.registration.get_lastname, user, bot)


    elif call.data == "yes_add_one_klass":
        bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Введите ваш класс:\n(пример: 1A)")
        # user = Users.objects.filter(chat_id=call.from_user.id)[0]
        user.groups.clear()
        bot.register_next_step_handler(call.message, tgbot.bot.registration.get_klass, cnt=1, bot=bot)
    elif call.data == "yes_add_two_klass":
        bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Введите ваш первый класс:\n(пример: 1A)")
        # user = Users.objects.filter(chat_id=call.message.chat.id)[0]
        user.groups.clear()
        bot.register_next_step_handler(call.message, tgbot.bot.registration.get_klass, cnt=2, bot=bot)
    elif call.data == "no_add_klass":
        bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Регистрация прошла успешно!")
        bot.send_message(call.message.chat.id, help_list_user)


    elif call.data == "report_evacuation":
        bot.send_message(call.message.chat.id,
                         "Введите класс, который вы эвакуировали:\n(пример: 1А)")
        evacuation = Evacuation()
        # user = Users.objects.filter(chat_id=call.from_user.id)[0]
        evacuation.teacher = user
        bot.register_next_step_handler(call.message, report_evacuation_klass, evacuation)

    elif call.data == "report_evacuation_chek_yes":
        # user = Users.objects.filter(chat_id=call.from_user.id)[0]
        evacuation = Evacuation.objects.get(teacher=user)
        evacuation.status = '1'
        evacuation.date = datetime.now()
        evacuation.save()

        users = Users.objects.filter(is_staff=True)
        kl_ruk = Users.objects.filter(groups=evacuation.klass)
        mess = f'{evacuation.klass} эвакуировал(а) {user.last_name} {user.first_name} {user.surename}\n{evacuation.amount} чел. успешно\n{evacuation.missing} чел. недосчитано'
        for u in users:
            if u.has_perm('tgbot.evacuate'):
                try:
                    bot.send_message(u.chat_id, mess)
                except:
                    pass
        for u in kl_ruk:
            if u.admin_verification:
                try:
                    print(u.chat_id)
                    bot.send_message(u.chat_id, mess)
                except:
                    pass
        bot.send_message(call.message.chat.id, "Информация отправлена администратору!")

    elif call.data == "report_evacuation_chek_no":
        # user = Users.objects.filter(chat_id=call.from_user.id)[0]
        try:
            evacuation = Evacuation.objects.get(teacher=user)
            evacuation.delete()
        except:
            pass
        bot.send_message(call.message.chat.id, "Введите верные данные:")
        bot.send_message(call.message.chat.id, "Введите класс, который вы эвакуировали:\n(пример: 1А)")
        evacuation = Evacuation()
        evacuation.teacher = user
        bot.register_next_step_handler(call.message, report_evacuation_klass, evacuation)


    elif call.data == "report_terror":
        report_terror_status(call)

    elif call.data == "report_terror_status_1":
        evacuation = Evacuation()
        evacuation.status = '1'
        # user = Users.objects.filter(chat_id=call.from_user.id)[0]
        evacuation.teacher = user
        bot.send_message(call.message.chat.id,
                         "Введите класс, который вы эвакуировали:\n(пример: 1А)")
        bot.register_next_step_handler(call.message, report_terror_klass, evacuation)
    elif call.data == "report_terror_status_2":
        evacuation = Evacuation()
        evacuation.status = '2'
        # user = Users.objects.filter(chat_id=call.from_user.id)[0]
        evacuation.teacher = user
        bot.send_message(call.message.chat.id,
                         "Введите класс, который вы забаррикадировали:\n(пример: 1А)")
        bot.register_next_step_handler(call.message, report_terror_klass, evacuation)

    elif call.data == "report_terror_chek_yes":
        # user = Users.objects.filter(chat_id=call.from_user.id)[0]
        evacuation = Evacuation.objects.get(teacher=user)
        evacuation.save()
        #####################################
        bot.send_message(call.message.chat.id, "Хорошо")
    elif call.data == "report_terror_chek_no":
        # user = Users.objects.filter(chat_id=call.from_user.id)[0]
        try:
            evacuation = Evacuation.objects.filter(teacher=user)[0]
            evacuation.delete()
        except:
            pass
        bot.send_message(call.message.chat.id, "Введите верные данные:")
        report_terror_status(call)


    elif call.data.split('*')[0] == 'missing':
        calldata = call.data.split('*')
        if calldata[1] == 'klass':
            bot.edit_message_text(chat_id=user.chat_id, message_id=call.message.message_id, text=call.message.text)
            tgbot.bot.missing.rolling(user, bot, klass_name=calldata[2], i=0)
        elif (calldata[1] == 'student') and True: #(calldata[5] > calldata[3]):
            i = int(calldata[3])
            klass_name = calldata[2]
            klass = Group.objects.filter(name=klass_name)[0]
            student = Students.objects.filter(klass=klass)[i]
            if calldata[4] == 'p':
                student.presence = True
                missing = Missing.objects.filter(date=date.today(), student=student)
                if len(missing) > 0:
                    missing.delete()
                    
            else:
                student.presence = False
                missing = Missing.objects.get_or_create(
                    date=date.today(),
                    student=student
                    )[0]
                if calldata[4] == 'b':
                    missing.reason = 'б'
                elif calldata[4] == 'u':
                    missing.reason = 'у'
                else:
                    missing.reason = 'н'
                accuracy = True
                missing.save()
                
            student.save()
            try:
                tgbot.bot.missing.rolling(user, bot, klass_name=calldata[2], i=i+1, message_id=call.message.message_id)
            except:
                tgbot.bot.missing.rolling(user, bot, klass_name=calldata[2], i=777,
                                          message_id=call.message.message_id)
                print('-------------------------------------------------------')
        elif calldata[1] == 'chek':
            klass_name = calldata[2]
            klass = Group.objects.filter(name=klass_name)[0]
            if calldata[3] == 'n':
                tgbot.bot.missing.rolling(user, bot, klass_name=calldata[2], i=0, message_id=call.message.message_id)
                tgbot.bot.missing.edit_absent_get_student(user, bot, klass)
            elif calldata[3] == 'y':
                bot.send_message(user.chat_id, f'Проверка окончена.')
                bot.edit_message_text(chat_id=user.chat_id, message_id=call.message.message_id, text=call.message.text)
        elif calldata[1] == 'edit':
            klass_name = calldata[3]
            klass = Group.objects.filter(name=klass_name)[0]
            if calldata[2] == 'get':
                tgbot.bot.missing.edit_absent_get_student(user, bot, klass)
            elif calldata[2] == 'student':
                tgbot.bot.missing.edit_absent_get_date(user=user, bot=bot, klass=klass, stud_id=calldata[4],
                                                       message_id=call.message.message_id)
            elif calldata[2] == 'date':
                tgbot.bot.missing.edit_absent_get_reason(user=user, bot=bot, klass=klass, stud_id=calldata[4],
                                                         date=calldata[5], message_id=call.message.message_id)
            elif calldata[2] == 'reason':
                tgbot.bot.missing.edit_absent_bd(user=user, bot=bot, klass=klass, stud_id=calldata[4],
                                                        dat=calldata[5], reason=calldata[6],
                                                        message_id=call.message.message_id)






    # content_type = ContentType.objects.get_for_model(Users)
    # print(1)
    # my_permission = Permission.objects.create(codename='evacuate',
    #                                           name='evacuate',
    #                                           content_type=content_type)
    # print(2)
    # # my_group = Group.objects.create(name='My Group')
    # # my_group.permissions = [my_permission]
@bot.message_handler(commands=['evacuation'])
def evacuation(message):
    user = Users.objects.filter(chat_id=message.chat.id)[0]
    if user.admin_verification:
        if user.has_perm('tgbot.evacuate'):
            users = Users.objects.filter(admin_verification=True)
            for u in users:
                keyboard = types.InlineKeyboardMarkup()
                key = types.InlineKeyboardButton(text='Нажмите для отчёта', callback_data='report_evacuation')
                keyboard.add(key)
                bot.send_message(u.chat_id,
                                 'Внимание! Запущен протокол эвакуации!\nПросьба без паники покинуть помещение, пользуясь схемами эвакуации и табличками "выход"!\nПосле эвакуации нажмите кнопку для отчёта!',
                                 reply_markup=keyboard)

        else:
            bot.send_message(message.from_user.id, 'Запрос отправлен администраторам!')
            users = Users.objects.all()
            for u in users:
                if u.has_perm('tgbot.evacuate'):
                    bot.send_message(u.chat_id,
                                     f'{user.last_name} {user.first_name} {user.surename}, запустил evacution!\nЗапрашивает эвакуацию!\nДля подтверждения введите /evacuation!')

    else:
        bot.send_message(message.chat.id, 'Ваша учётная запись не проверена администратором.')



def report_evacuation_klass(message, evacuation):
    evacuation.klass = Group.objects.filter(name=message.text.upper())[0]
    bot.send_message(message.from_user.id, "Введите количество эвакуированных с вами детей:")
    bot.register_next_step_handler(message, report_evacuation_amount, evacuation)


def report_evacuation_amount(message, evacuation):
    evacuation.amount = int(message.text)
    evacuation.before = Students.objects.filter(klass=evacuation.klass, presence=True).count()
    evacuation.missing = evacuation.before - evacuation.amount
    bot.send_message(message.from_user.id, "Введите кабинет, из которого вы эвакуировались:")
    bot.register_next_step_handler(message, report_evacuation_klass_room, evacuation)


def report_evacuation_klass_room(message, evacuation):
    evacuation.klass_room = message.text
    mess = 'Должны присутствовать:\n'
    for i, x in enumerate(Students.objects.filter(klass=evacuation.klass, presence=True)):
        mess += f'{i + 1}. {x.last_name} {x.first_name}\n'
    mess += '\nДолжны отсутствовать:\n'
    for i, x in enumerate(Students.objects.filter(klass=evacuation.klass, presence=False)):
        mess += f'{i + 1}. {x.last_name} {x.first_name}\n'
    bot.send_message(message.from_user.id, mess)
    bot.send_message(message.from_user.id, "Введите дополнительную информацию:\n(Если ничего не хотите вводить, то напишите '-')")
    bot.register_next_step_handler(message, report_evacuation_note, evacuation)



def report_evacuation_note(message, evacuation):
    evacuation.note = message.text
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='report_evacuation_chek_yes')
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='report_evacuation_chek_no')
    keyboard.add(key_yes, key_no)
    bot.send_message(message.from_user.id,
                     f'''{evacuation.teacher.last_name} {evacuation.teacher.first_name} {evacuation.teacher.surename} эвакуировал(а):'
                         {evacuation.klass} класс
                         в количестве: {evacuation.amount} чел.
                         из {evacuation.klass_room}
                         Должно быть: {evacuation.before}
                         Отсутствует: {evacuation.missing}
                         Дополнительная информация:
                         {evacuation.note}''',
                     reply_markup=keyboard)
    evacuation.save()




@bot.message_handler(commands=['terror'])
def evacuation(message):
    user = Users.objects.filter(chat_id=message.chat.id)[0]
    if user.admin_verification:
        if user.has_perm('tgbot.evacuate'):
            users = Users.objects.all()
            for u in users:
                try:
                    keyboard = types.InlineKeyboardMarkup()
                    key = types.InlineKeyboardButton(text='Нажмите для отчёта', callback_data='report_terror')
                    keyboard.add(key)
                    bot.send_message(u.chat_id,
                                     'Внимание! Запущен протокол эвакуации или баррикадирования!\nПросьба без паники покинуть помещение, пользуясь схемами эвакуации и табличками "выход"!\n'
                                     'Или забаррикадироваться в ближайшем кабинете!\nПосле эвакуации или баррикадирования нажмите кнопку для отчёта!',
                                     reply_markup=keyboard)
                except:
                    pass
                print(0)

        else:
            bot.send_message(message.from_user.id, 'Запрос отправлен администраторам!')
            users = Users.objects.all()
            for u in users:
                if u.has_perm('tgbot.evacuate'):
                    bot.send_message(u.chat_id,
                                     f'{user.last_name} {user.first_name} {user.surename}, запустил terror!\nЗапрашивает эвакуацию или барикадирование!\nДля подтверждения введите /terror!')

    else:
        bot.send_message(message.chat.id, 'Ваша учётная запись не проверена администратором.')


def report_terror_status(call):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Эвакуировались', callback_data='report_terror_status_1')
    key_no = types.InlineKeyboardButton(text='Забаррикадировались', callback_data='report_terror_status_2')
    keyboard.add(key_yes)
    keyboard.add(key_no)
    bot.send_message(call.message.chat.id, 'Выберите действие!', reply_markup=keyboard)


def report_terror_klass(message, evacuation):
    evacuation.klass = Group.objects.filter(name=message.text.upper())[0]
    if evacuation.status == '1':
        bot.send_message(message.from_user.id, "Введите количество эвакуированных с вами детей:")
    elif evacuation.status == '2':
        bot.send_message(message.from_user.id, "Введите количество забаррикадированных с вами детей:")
    else:
        bot.send_message(message.from_user.id, "Ошибка статуса:")

    bot.register_next_step_handler(message, report_terror_amount, evacuation)


def report_terror_amount(message, evacuation):
    evacuation.amount = int(message.text)
    evacuation.before = Students.objects.filter(klass=evacuation.klass, presence=True).count()
    evacuation.missing = evacuation.before - evacuation.amount
    if evacuation.status == '1':
        bot.send_message(message.from_user.id, "Введите кабинет, из которого вы эвакуировались:")
    elif evacuation.status == '2':
        bot.send_message(message.from_user.id, "Введите кабинет, в котором вы забаррикодировались:")
    else:
        bot.send_message(message.from_user.id, "Ошибка статуса:")
    bot.register_next_step_handler(message, report_terror_klass_room, evacuation)


def report_terror_klass_room(message, evacuation):
    evacuation.klass_room = message.text
    mess = 'Должны присутствовать:\n'
    for i, x in enumerate(Students.objects.filter(klass=evacuation.klass, presence=True)):
        mess += f'{i+1}. {x.last_name} {x.first_name}\n'
    mess += '\nДолжны отсутствовать:\n'
    for i, x in enumerate(Students.objects.filter(klass=evacuation.klass, presence=False)):
        mess += f'{i+1}. {x.last_name} {x.first_name}\n'
    bot.send_message(message.from_user.id, mess)
    bot.send_message(message.from_user.id, "Введите дополнительную информацию:\n(Если ничего не хотите вводить, то напишите '-')")
    bot.register_next_step_handler(message, report_terror_note, evacuation)



def report_terror_note(message, evacuation):
    evacuation.note = message.text
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='report_terror_chek_yes')
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='report_terror_chek_no')
    keyboard.add(key_yes, key_no)
    bot.send_message(message.from_user.id,
                     f'''{evacuation.teacher.last_name} {evacuation.teacher.first_name} {evacuation.teacher.surename} {evacuation.get_status_display()}(а):
                     {evacuation.klass} класс
                     в количестве: {evacuation.amount} чел.
                     из {evacuation.klass_room}
                     Должно быть: {evacuation.before}
                     Отсутствует: {evacuation.missing}
                     Дополнительная информация:
                     {evacuation.note}''',
                     reply_markup=keyboard)
    evacuation.save()

# bot.polling(none_stop=True)
while True:
    try:
        bot.polling(none_stop=True)
    except:
        continue