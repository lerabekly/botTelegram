import telebot
from newsapi import NewsApiClient
from bd import *
from config import token
from telebot import types
bot = telebot.TeleBot(token, parse_mode=None)
newsapi = NewsApiClient(api_key='4b9cb39ee8394fe2bc7c47cf875895ae')

@bot.message_handler(commands=['start'])

def send_welcome(message):
  userid = [message.chat.id]
  connect = sqlite3.connect('bd.db')
  cursor = connect.cursor()
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btnNews = types.KeyboardButton('Новости')
  btnSub = types.KeyboardButton('Мои подписки')
  btnCateg = types.KeyboardButton('Категории')
  markup.add(btnCateg, btnNews, btnSub)

  user = cursor.execute('SELECT * FROM users WHERE tg_id = ?;', (userid) ).fetchall()

  if not user:
   cursor.execute('''INSERT INTO users('tg_id') VALUES(?);''', userid)
   connect.commit()
   bot.reply_to(message, "Вы успешно зарегистрированы ", reply_markup=markup)
  else:
   bot.reply_to(message, "Вы уже зарегистрированы", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def bot_message(message):
  print(message.text)
  if message.chat.type == 'private':
    if message.text == 'Категории':
      markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
      connect = sqlite3.connect('bd.db')
      cursor = connect.cursor()
      categories = cursor.execute('SELECT * FROM categories ;').fetchall()
      i=0
      while i<len(categories):
          name = types.KeyboardButton("Подписаться на " + categories[i][1])
          markup.add(name)
          i=i+1
      back = types.KeyboardButton('Вернуться')
      markup.add(back)

      bot.reply_to(message, "Подпишитесь на категории:", reply_markup=markup)

  if message.chat.type == 'private':
    subs = "Подписаться"
    if message.text.startswith(subs):
        userid = [message.chat.id]
        connect = sqlite3.connect('bd.db')
        cursor = connect.cursor()
        id = cursor.execute('SELECT id FROM users WHERE tg_id=?;', (userid)).fetchone()
        # ту стр
        id=str(id[0])
        sub = cursor.execute('SELECT * FROM subscribes INNER JOIN categories ON categories.id = subscribes.category_id WHERE user_id = ?;',(id)).fetchall()
        arrSub = []
        i = 0
        while i <len(sub):
            arrSub.append(sub[i][3])
            i=i+1

        i=0
        count=0
        forWhat = message.text[15:]
        while i<len(arrSub):

            if forWhat == arrSub[i]:
                count=count+1
            i=i+1
        if count ==0:
            categ_id = cursor.execute('SELECT id FROM categories WHERE name=?;', (forWhat,)).fetchall()
            cursor.execute('''INSERT INTO subscribes('user_id', 'category_id') VALUES(?,?);''', (id, categ_id[0][0]))
            connect.commit()
            bot.reply_to(message, "Вы успешно подписаны")
        else:
            bot.reply_to(message, "Вы уже подписаны")

    if message.chat.type == 'private':
          if message.text == 'Мои подписки':
              markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
              userid = [message.chat.id]
              connect = sqlite3.connect('bd.db')
              cursor = connect.cursor()
              id = cursor.execute('SELECT id FROM users WHERE tg_id=?;', (userid)).fetchone()
              id = str(id[0])
              sub = cursor.execute('SELECT * FROM subscribes INNER JOIN categories ON categories.id = subscribes.category_id WHERE user_id = ?;',(id)).fetchall()
              arrSub = []
              i = 0
              while i < len(sub):
                  arrSub.append(sub[i][3])
                  i = i + 1
              i = 0
              while i < len(arrSub):
                  name = str(arrSub[i])
                  name = types.KeyboardButton("Отписаться от " + arrSub[i])
                  markup.add(name)

                  i = i + 1
              back = types.KeyboardButton('Вернуться')
              markup.add(back)
              bot.reply_to(message, "Мои подписки:", reply_markup=markup)

    if message.chat.type == 'private':
        subs = "Отписаться"
        if message.text.startswith(subs):
            userid = [message.chat.id]
            connect = sqlite3.connect('bd.db')
            cursor = connect.cursor()
            id = cursor.execute('SELECT id FROM users WHERE tg_id=?;', (userid)).fetchone()
            id=str(id[0])
            forWhat = message.text[14:]
            categ_id = cursor.execute('SELECT id FROM categories WHERE name=?;', (forWhat,)).fetchall()
            categ_id = categ_id[0][0]
            have = cursor.execute('SELECT * FROM subscribes WHERE user_id = ? and category_id = ?;',(id, categ_id)).fetchone()

            if not have:
                bot.reply_to(message, "Вы не подписаны")
            else:
                cursor.execute('DELETE FROM subscribes WHERE user_id = ? and category_id = ?;',(id, categ_id))
                connect.commit()

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                sub = cursor.execute(
                    'SELECT * FROM subscribes INNER JOIN categories ON categories.id = subscribes.category_id WHERE user_id = ?;',
                    (id)).fetchall()
                arrSub = []
                i = 0
                while i < len(sub):
                    arrSub.append(sub[i][3])
                    i = i + 1
                i = 0
                while i < len(arrSub):
                    name = str(arrSub[i])

                    name = types.KeyboardButton("Отписаться от " + arrSub[i])
                    markup.add(name)

                    i = i + 1
                back = types.KeyboardButton('Вернуться')
                markup.add(back)

                bot.reply_to(message, "Вы успешно отписались", reply_markup=markup)


    if message.chat.type == 'private':
          if message.text == 'Новости':
              userid = [message.chat.id]
              connect = sqlite3.connect('bd.db')
              cursor = connect.cursor()
              id = cursor.execute('SELECT id FROM users WHERE tg_id=?;', (userid)).fetchone()
              id = str(id[0])
              sub = cursor.execute('SELECT * FROM subscribes INNER JOIN categories ON categories.id = subscribes.category_id WHERE user_id = ?;',(id)).fetchall()

              i=0
              while i < len(sub):
                  top_headlines = newsapi.get_top_headlines(category=f'{sub[i][3]}', language='ru', country='ru', page=1 , page_size=1)
                  bot.send_message(message.chat.id,f'Категория:{sub[i][3]}\nЗаголовок: {top_headlines["articles"][0]["title"]}\n {top_headlines["articles"][0]["url"]}')
                  i = i + 1

  if message.chat.type == 'private':
    if message.text == 'Вернуться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btnNews = types.KeyboardButton('Новости')
        btnSub = types.KeyboardButton('Мои подписки')
        btnCateg = types.KeyboardButton('Категории')
        markup.add(btnCateg, btnNews, btnSub)
        bot.reply_to(message, "Что надо?", reply_markup=markup)

bot.infinity_polling(none_stop = True)