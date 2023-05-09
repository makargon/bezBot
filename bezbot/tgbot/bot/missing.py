from telebot import types
from tgbot.models import Users, Group, Students, Missing
from datetime import date, timedelta

def absent(user, bot):
    'Вывод доступных классов для простановки фактов отсутствия'
    id = user.chat_id
    if len(user.groups.all()) == 0:
        bot.send_message(id, 'У вас нет класса.')
    elif len(user.groups.all()) == 1:
        keyboard = types.InlineKeyboardMarkup()
        key = types.InlineKeyboardButton(text=f'{user.groups.all()[0]}',
                                           callback_data=f'missing*klass*{user.groups.all()[0]}')
        keyboard.add(key)
        sent = bot.send_message(id, 'Давайте проверим присутствие учеников в классе:', reply_markup=keyboard)
    elif len(user.groups.all()) == 2:
        keyboard = types.InlineKeyboardMarkup()
        key_1 = types.InlineKeyboardButton(text=f'{user.groups.all()[0]}', callback_data=f'missing*klass*{user.groups.all()[0]}')
        key_2 = types.InlineKeyboardButton(text=f'{user.groups.all()[1]}', callback_data=f'missing*klass*{user.groups.all()[1]}')
        keyboard.add(key_1, key_2)
        sent = bot.send_message(id, 'Давайте проверим присутствие учеников в классе:', reply_markup=keyboard)
        # bot.register_next_step_handler(sent, roling, user=user, bot=bot)


def rolling(user, bot, klass_name, i, message_id=0):
    'Рулетка, выводящяя ФИ ученика в классе по i и клавиатуру с причинами отсутствия, при id=777, выводит весь класс'

    klass = Group.objects.filter(name=klass_name)[0]

    cnt = len(Students.objects.filter(klass=klass))
    if i != 777:
        student = Students.objects.filter(klass=klass)[i]
        # mess = 'Должны присутствовать:\n'
        # for i, x in enumerate(klass):
        #     mess += f'{i + 1}. {x.last_name} {x.first_name}\n'

        keyboard = types.InlineKeyboardMarkup()
        key_1 = types.InlineKeyboardButton(text='❌Болеет',
                                           callback_data=f'missing*student*{klass_name}*{i}*b*{cnt}')
        key_2 = types.InlineKeyboardButton(text='❌Неуваж.',
                                           callback_data=f'missing*student*{klass_name}*{i}*n*{cnt}')
        key_3 = types.InlineKeyboardButton(text='❌Уваж.',
                                           callback_data=f'missing*student*{klass_name}*{i}*u*{cnt}')
        key_4 = types.InlineKeyboardButton(text='✅Присутствует✅',
                                           callback_data=f'missing*student*{klass_name}*{i}*p*{cnt}')
        keyboard.add(key_1, key_2, key_3)
        keyboard.add(key_4)
        if message_id == 0: # если сообщение первое, отправляет новое, в противном случае редактирурет
            bot.send_message(user.chat_id, f'{i+1}. {student.last_name} {student.first_name}', reply_markup=keyboard)
        else:
            bot.edit_message_text(chat_id=user.chat_id, message_id=message_id, text=f'{i+1}. {student.last_name} {student.first_name}', reply_markup=keyboard)

    elif i == 777:
        student = Students.objects.filter(klass=klass)
        mess = f'{klass_name}:\n'
        for i, x in enumerate(student):
            mess += f'{i + 1}. '
            if x.presence == True:
                rise = ''
                mess += f'✅ '
            else:
                mess += f'❌ '
                rise = Missing.objects.filter(student=x, date=date.today())[0].get_reason_display()
                if rise == "неуважительная":
                    rise = f'             {rise}😡\n'
                elif rise == "уважительная":
                    rise = f'             {rise}😌\n'
                elif rise == "болеет":
                    rise = f'             {rise}🤒\n'
            mess += f'{x.last_name} {x.first_name}\n{rise}'

        keyboard = types.InlineKeyboardMarkup()
        key_1 = types.InlineKeyboardButton(text='❌',
                                           callback_data=f'missing*chek*{klass_name}*n*{cnt}')
        key_2 = types.InlineKeyboardButton(text='✅',
                                           callback_data=f'missing*chek*{klass_name}*y*{cnt}')
        keyboard.add(key_1, key_2)
        bot.edit_message_text(chat_id=user.chat_id, message_id=message_id, text=mess, reply_markup=keyboard)

def edit_absent(user, bot):
    'Редактирование пропуска по фамилии(Не доделано)'
    id = user.chat_id
    if len(user.groups.all()) == 0:
        bot.send_message(id, 'У вас нет класса.')
    elif len(user.groups.all()) == 1:
        keyboard = types.InlineKeyboardMarkup()
        key = types.InlineKeyboardButton(text=f'{user.groups.all()[0]}',
                                           callback_data=f'missing*edit*get*{user.groups.all()[0]}')
        keyboard.add(key)
        sent = bot.send_message(id, 'Давайте проверим присутствие учеников в классе:', reply_markup=keyboard)
    elif len(user.groups.all()) == 2:
        keyboard = types.InlineKeyboardMarkup()
        key_1 = types.InlineKeyboardButton(text=f'{user.groups.all()[0]}', callback_data=f'missing*edit*get*{user.groups.all()[0]}')
        key_2 = types.InlineKeyboardButton(text=f'{user.groups.all()[1]}', callback_data=f'missing*edit*get*{user.groups.all()[1]}')
        keyboard.add(key_1, key_2)
        sent = bot.send_message(id, 'Давайте проверим присутствие учеников в классе:', reply_markup=keyboard)

def edit_absent_get_student(user, bot, klass):
    id = user.chat_id
    student = Students.objects.filter(klass=klass)
    keyboard = types.InlineKeyboardMarkup()
    for i, x in enumerate(student):
        key = types.InlineKeyboardButton(text=f'{i+1}. {x.last_name} {x.first_name}',
                                           callback_data=f'missing*edit*student*{klass}*{i}')
        keyboard.add(key)
    sent = bot.send_message(id, klass, reply_markup=keyboard)

def edit_absent_get_date(user, bot, klass, stud_id, message_id):
    id = user.chat_id
    student = Students.objects.filter(klass=klass)[int(stud_id)]
    keyboard = types.InlineKeyboardMarkup()
    date_list = [(date.today() - timedelta(days=2)),
                 (date.today() - timedelta(days=1)),
                 date.today(),
                 (date.today() + timedelta(days=1)),
                 (date.today() + timedelta(days=2)),
                 ]
    for i, x in enumerate(date_list):
        key = types.InlineKeyboardButton(text=x.strftime("%Y-%m-%d"),
                                           callback_data=f'missing*edit*date*{klass}*{stud_id}*{x.strftime("%Y-%m-%d")}')
        keyboard.add(key)
    sent = bot.edit_message_text(chat_id=id, text=f'{student.last_name} {student.first_name}', reply_markup=keyboard, message_id=message_id)


def edit_absent_get_reason(user, bot, klass, stud_id, message_id, date):
    id = user.chat_id
    student = Students.objects.filter(klass=klass)[int(stud_id)]
    keyboard = types.InlineKeyboardMarkup()
    key_1 = types.InlineKeyboardButton(text='❌Болеет',
                                       callback_data=f'missing*edit*reason*{klass}*{stud_id}*{date}*b')
    key_2 = types.InlineKeyboardButton(text='❌Неуваж.',
                                       callback_data=f'missing*edit*reason*{klass}*{stud_id}*{date}*n')
    key_3 = types.InlineKeyboardButton(text='❌Уваж.',
                                       callback_data=f'missing*edit*reason*{klass}*{stud_id}*{date}*u')
    key_4 = types.InlineKeyboardButton(text='✅Присутствует✅',
                                       callback_data=f'missing*edit*reason*{klass}*{stud_id}*{date}*p')
    keyboard.add(key_1, key_2, key_3)
    keyboard.add(key_4)
    sent = bot.edit_message_text(chat_id=id, text=f'{student.last_name} {student.first_name}', reply_markup=keyboard,
                                 message_id=message_id)

def edit_absent_bd(user, bot, klass, stud_id, message_id, dat, reason):
    id = user.chat_id
    print(dat[:4], dat[5:7], dat[8:10])
    dat = date(year=int(dat[:4]), month=int(dat[5:7]), day=int(dat[8:10]))
    print(dat)
    student = Students.objects.filter(klass=klass)[int(stud_id)]
    missing = Missing.objects.filter(student=student, date=dat)
    if reason == 'p':
        missing.delete()
        bot.edit_message_text(chat_id=id, text=f'{dat} {student.last_name} {student.first_name} ✅', message_id=message_id)
    else:
        if reason == 'n':
            reason = 'н'
        elif reason == 'b':
            reason = 'б'
        else:
            reason = 'у'
        if len(missing) == 0:
            Missing.objects.get_or_create(student=student, date=dat, reason=reason)
        else:
            missing.reason = reason
            missing.save()
        bot.edit_message_text(chat_id=id, text=f'{dat} {student.last_name} {student.first_name} ({reason})', message_id=message_id)