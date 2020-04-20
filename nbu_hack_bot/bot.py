import telebot
import config
import random
import urllib
import model
import os

from telebot import types

from flask import Flask, request

TOKEN = config.TOKEN
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# handler for start command, sends welcome message and a cute sticker
@bot.message_handler(commands=['start'])
def welcome(message):
	sti = open('sticker.webp','rb')

	bot.send_sticker(message.chat.id, sti)
	bot.send_message(message.chat.id, "Привет, {0.first_name}!\nЯ-<b>{1.first_name} bot</b>, созданный командой Belka DS.\nОтправьте мне картинку банкноты и я ее классифицирую".format(message.from_user, bot.get_me()), parse_mode="html")

# handler for text, asks user to send image, not a text
@bot.message_handler(content_types=['text'])
def text_handler(message):
	bot.send_message(message.chat.id, 'Не текст, картинку ;)')

# handler for images, that uses our model and give predictions
@bot.message_handler(content_types=['photo'])
def image_handler(message):
	bot.send_message(message.chat.id, "Вы отправили картинку")
	bot.send_photo(message.chat.id, message.photo[-1].file_id)

	# get access to the photo and download it as 'image.jpg'
	photo_id = message.photo[-1].file_id
	file_path = bot.get_file(photo_id).file_path
	image_url = "https://api.telegram.org/file/bot{0}/{1}".format(config.TOKEN, file_path)
	urllib.request.urlretrieve(image_url, "image.jpg") 

	# sending information about process
	bot.send_message(message.chat.id, "Картинка успешно сохранена")
	bot.send_message(message.chat.id, "Обрабатываем...")

	# process image and get prediction as a string
	label = model.image_processing('image.jpg')
	bot.send_message(message.chat.id, label)
	print('Обработка завершена')


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

# for webhook
@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://thawing-ravine-44312.herokuapp.com/' + TOKEN)
    return "!", 200

if __name__ == "main":
	server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
