import telebot
from telebot import types
from django.conf import settings
from tgbot.models import Users
import tgbot.bot.registration

bot = telebot.TeleBot(settings.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    n = message.from_user.first_name
    sn = message.from_user.last_name
    id = message.chat.id
    users = Users.objects.filter(chat_id = id)
    if len(users) == 1:
        user = users[0]
        print(user.get_group_permissions())
        if user.admin_verification:
            mess = f'Здравствуйте, <b>{user.last_name} {user.first_name} {user.surename}</b>'
            bot.send_message(message.chat.id, mess + '!\nВы являетесь администратором!',
                             parse_mode='html')
        else:
            mess = f'Здравствуйте, <b>{user.last_name} {user.first_name} {user.surename}</b>'
            bot.send_message(message.chat.id, mess, parse_mode='html')
    elif len(users) == 0:
        user = Users()
        user.chat_id = id
        user.username = f'{n} {sn}'
        user.admin_verification = False

        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text='Нажмите для начала регистрации', request_contact=True)
        keyboard.add(button_phone)
        sent = bot.send_message(id, "Здравствуйте! Вам необходимо зарегистрироваться.", reply_markup=keyboard)
        bot.register_next_step_handler(sent, tgbot.bot.registration.phone, user)


    print(users)
    print(message.chat.id, ': ', n, sn)