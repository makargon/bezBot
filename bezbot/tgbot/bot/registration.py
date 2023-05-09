from telebot import types
from tgbot.models import Users, Group

def phone(message, user, bot) :
    if message.contact is not None:
        keyboard2 = types.ReplyKeyboardRemove()
        user.phone_number = str(message.contact.phone_number)
        bot.send_message(message.chat.id, 'Вы успешно отправили свой номер.', reply_markup=keyboard2)
        print(str(message.contact.phone_number))
    sent = bot.send_message(message.chat.id, "Введите свою фамилию:")
    bot.register_next_step_handler(sent, get_lastname, user, bot)
def get_lastname(message, user, bot): # Получение имени с запросом фамилии
    user.last_name = message.text
    bot.send_message(message.from_user.id, "Введите своё имя:")
    bot.register_next_step_handler(message, get_name, user, bot)
def get_name(message, user, bot): # Получение фамилии с запросом отчества
    user.first_name = message.text
    bot.send_message(message.from_user.id, "Введите своё отчество:")
    bot.register_next_step_handler(message, get_surname, user, bot)
def get_surname(message, user, bot): # Получение Отчества с запросом классов
    user.surename = message.text
    user.save()


    keyboard = types.InlineKeyboardMarkup()
    key_yes1 = types.InlineKeyboardButton(text='У меня один класс', callback_data='yes_add_one_klass')
    key_yes2 = types.InlineKeyboardButton(text='У меня два класса', callback_data='yes_add_two_klass')
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no_add_klass')
    keyboard.add(key_yes1)
    keyboard.add(key_yes2)
    keyboard.add(key_no)

    bot.send_message(message.from_user.id, text="Вы являетесь классным руководителем?", reply_markup=keyboard)
    # bot.register_next_step_handler(message, get_klass, user)


def get_klass(message, cnt, bot):
    user = Users.objects.filter(chat_id=message.chat.id)[0]
    if cnt == 1:
        my_group = Group.objects.get_or_create(name=message.text.upper())[0]
        user.groups.add(my_group)
        user.save()
        bot.send_message(message.chat.id, "Давайте проверим:")
        keyboard = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text='Верно', callback_data='reg_yes')
        key_no = types.InlineKeyboardButton(text='Неверно', callback_data='reg_no')
        keyboard.add(key_yes)
        keyboard.add(key_no)
        mess = f'Давайте проверим: {user.last_name} {user.first_name} {user.surename}, Класс(ы): '
        for i in user.groups.all():
            mess += str(i) + ' '
        bot.send_message(message.from_user.id,
                         mess,
                         reply_markup=keyboard)
    elif cnt == 2:
        my_group = Group.objects.get_or_create(name=message.text.upper())[0]
        user.groups.add(my_group)
        bot.send_message(message.chat.id, "Введите ваш второй класс:\n(пример: 2A)")
        bot.register_next_step_handler(message, get_klass, cnt=1, bot=bot)
        user.save()
