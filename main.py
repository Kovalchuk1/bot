import telebot
import pandas as pd
from telebot import types
from io import BytesIO
import random
import time

bot = telebot.TeleBot('5994430411:AAEBf2QBrrgCylo4k6N7KWX-u48Wx7CDaGU', )
df = pd.DataFrame()
part_df = pd.DataFrame()
word = ''
options = []
value_mean = 4
a = 0
file_s = 0
test_df = pd.DataFrame({'word': ['apple', 'information', 'orange', 'home', 'program', 'sun'],
                        'translate': ['яблуко', 'інформація', 'помаранчевий', 'будинок', 'програма', 'сонце'],
                        'res': [0, 0, 0, 0, 0, 0],
                        'time_an': [0, 0, 0, 0, 0, 0],
                        'correct_an': [0, 0, 0, 0, 0, 0]})


def generate_question(dF):
    global word, options
    word = dF['word'].sample().values[0]
    if dF.shape[0] >=4:
        d = 3
    else:
        d = dF.shape[0] - 1
    options = dF.loc[dF['word'] != word, 'translate'].sample(n=d).tolist() + [dF.loc[dF['word'] == word, 'translate'].values[0]]
    print(options)
    random.shuffle(options)
    return word, options


def generate_question2():
    global word, options
    word = test_df[test_df['res'] == 0]['word'].sample().values[0]
    options = test_df.loc[test_df['word'] != word, 'translate'].sample(n=3).tolist() + [test_df.loc[test_df['word'] == word, 'translate'].values[0]]
    random.shuffle(options)
    return word, options

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Привіт. Перейдем до практики")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привіт. Я бот, який допоможе тобі у вивченні слів!", reply_markup=markup)


@bot.message_handler(content_types=['document'])
def handle_file(message):
    global df
    first_file = pd.DataFrame()
    if file_s == 1:
        df = pd.DataFrame()
    elif file_s == 2:
        first_file = df
        df = pd.DataFrame()
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    if len(downloaded_file) == 0:
        bot.send_message(message.chat.id, "Файл порожній. Надішліть, будь ласка, непорожній файл.")
    else:
        with open("word", 'wb') as new_file:
            new_file.write(downloaded_file)
        df = pd.read_csv(BytesIO(downloaded_file))
        df.columns = ['word', 'translate']
        df['repit'] = 0
        df['count_errors'] = 0
        bot.send_message(message.chat.id, "Файл отримано, можемо продовжувати.")
    if file_s == 2:
        df = pd.concat([first_file, df])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn2 = types.KeyboardButton('Правила бота')
    btn3 = types.KeyboardButton('Почати навчатись')
    markup.add(btn2, btn3)
    bot.send_message(message.from_user.id,
                     'Можемо переходити до навчання',
                     reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global options, word, start_time, end_time, a, value_mean, part_df, df, file_s
    if message.text == '👋 Привіт. Перейдем до практики':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Загрузить файл слів')
        btn2 = types.KeyboardButton('Правила бота')
        btn3 = types.KeyboardButton('Почати навчатись')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, 'Якщо ти новий користувач тобі потрібно загрузити файл слів, які хочеш вивчати', reply_markup=markup)

    elif message.text == 'Правила бота':
        bot.send_message(message.from_user.id, '\xd0 Все просто, якщо будеш дотримуватись моїх прохань:\n 1. Використовуй формат файла саме, який вказано та формат заповнення, щоб я міг допомогти із вивченням\n 2. Ти маєш розуміти,що я тільки допомагаю генерувати слова для вивчення, тому цього не достатньо, щоб володіти повноцінно мовою, яку вивчаєш. \n 3. Я зможу приносити тобі користь, ящко ти витрачатимеш кожного дня по 15-20 хвилин на вивчення.' , parse_mode='Markdown')

    elif message.text == 'Почати навчатись':
        if value_mean == 0:
            bot.send_message(message.chat.id, f"Давай пройдемо пробний тест для покращення твого навчання!")
            word, options = generate_question2()
            test_df.loc[test_df['word'] == word, 'res'] = 1
            a = 1
            markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
            for option in options:
                markup.add(telebot.types.KeyboardButton(option))
            start_time = time.perf_counter()
            bot.send_message(message.chat.id, f"Який переклад слова '{word}'?", reply_markup=markup)

        if df.empty:
            bot.send_message(message.chat.id, "Ви не надіслали файл слів або він порожній. Надішліть, будь ласка, повторо файл.")
        else:
            if value_mean != 0:
                if part_df.empty:
                    if df.shape[0] <= 5:
                        part_df = df[['word', 'translate']]
                    else:
                        part_df = df.loc[df['repit'] == 0, ['word', 'translate']].sample(n=5)
                    for index, row in part_df.iterrows():
                        word = row['word']
                        translate = row['translate']
                        mask = (df['word'] == word) & (df['translate'] == translate)
                        df.loc[mask, 'repit'] = 1

                    part_df['rating'] = 2
                    part_df['repit'] = 0
                    part_df['count_errors'] = 0

                word, options = generate_question(part_df)

                markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
                for option in options:
                    markup.add(telebot.types.KeyboardButton(option))
                start_time = time.perf_counter()
                bot.send_message(message.chat.id, f"Який переклад слова '{word}'?", reply_markup=markup)

    elif message.text in options:
        if a == 1:
            df2 = test_df
        else:
            df2 = part_df

        answer = message.text
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        correct_answer = df2.loc[df2['word'] == word, 'translate'].values[0]
        if answer == correct_answer:
            if a == 1:
                test_df.loc[test_df['word'] == word, 'correct_an'] = 1
                test_df.loc[test_df['word'] == word, 'time_an'] = execution_time
            if a == 0:

                s = 0
                if execution_time < value_mean: s += 0.5
                else: s += -0.5

                part_df.loc[part_df['word'] == word, 'rating'] = part_df.loc[part_df['word'] == word, 'rating'] - 1 - s

            bot.reply_to(message, 'Вірно!')
            bot.send_animation(message.chat.id, 'https://media.tenor.com/5lLcKZgmIhgAAAAC/american-psycho-patrick-bateman.gif')
        else:
            if a == 0:
              s = 0
              if execution_time < value_mean: s -= 0.5
              else: s += 0.5
              part_df.loc[part_df['word'] == word, 'rating'] = part_df.loc[part_df['word'] == word, 'rating'] + 3 + s
              part_df.loc[part_df['word'] == word, 'count_errors'] += 1
            bot.reply_to(message, f'Неправильно. Правильний варіант: {correct_answer}.')
            bot.send_animation(message.chat.id, 'https://media.tenor.com/upPmgF2cbWQAAAAd/american-psycho-joker.gif')

        #перевіряємо чи є ел з рейтингом 0, якщо так слово вивчене і замінюємо на інше із df
        if a == 0:
            if (part_df['rating'] <= 0).sum() > 0:
                filtered_part_df = part_df[part_df['rating'] <= 0]
                merged_df = df.merge(filtered_part_df[['word', 'translate', 'count_errors']], on=['word', 'translate'], how='left')
                merged_df['count_errors'] = merged_df['count_errors_y'].fillna(merged_df['count_errors_x'])
                merged_df = merged_df.drop(columns=['count_errors_x', 'count_errors_y'])

                df = merged_df
                part_df = part_df[part_df['rating'] > 0]
                if (df['repit'] == 0).count() > 0:
                    mask2 = df['repit'] == 0
                    new_rows = df.loc[mask2, ['word', 'translate']]
                    n_rows_to_add = min(5 - len(part_df), len(new_rows))

                    if n_rows_to_add > 0:
                        new_rows_to_add = new_rows.head(n_rows_to_add).copy()
                        new_rows_to_add['rating'] = 2
                        new_rows_to_add['repit'] = 0
                        new_rows_to_add['count_errors'] = 0
                        part_df = pd.concat([part_df, new_rows_to_add])
                        df.loc[new_rows_to_add.index, 'repit'] = 1
                print(df)
                print(part_df)
            if part_df.shape[0] == 0 and (df['repit'] == 0).sum() == 0:

                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    btn1 = types.KeyboardButton('Загрузить новий файл слів')
                    btn12 = types.KeyboardButton('Додати слова до наявного файлу')
                    btn2 = types.KeyboardButton('Правила бота')
                    btn3 = types.KeyboardButton('Повторити складні для мене слова')

                    markup.add(btn1, btn12, btn2, btn3)
                    bot.reply_to(message,
                                 'Здається заплановані слова для вивчення уже засвоєні тобою. Але для кращого засвоєння пропоную повторити найскладніші для тебе слова або перейти до нових слів)', reply_markup=markup)
        if a == 1:
            if df2[df2['res'] == 0]['res'].count() != 0:

                word, options = generate_question2()
                test_df.loc[test_df['word'] == word, 'res'] = 1
                markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
                for option in options:
                    markup.add(telebot.types.KeyboardButton(option))
                start_time = time.perf_counter()
                bot.send_message(message.chat.id, f"Який переклад слова '{word}'?", reply_markup=markup)

            else:

                if a == 1:
                    print(test_df)
                    avg = test_df[test_df['correct_an'] == 1]['time_an'].mean()
                    value_mean = test_df[test_df['correct_an'] == 1]['time_an'].std() + avg
                a = 0
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton('Загрузить файл слів')
                btn2 = types.KeyboardButton('Правила бота')
                btn3 = types.KeyboardButton('Почати навчатись')
                markup.add(btn1, btn2, btn3)
                bot.send_message(message.from_user.id, 'Тепер можемо перейти до найцікавішого', reply_markup=markup)
        else:
            if value_mean != 0 and (df['repit'] == 0).sum() != 0:
                if part_df.empty:
                    if df.shape[0] <= 5:
                        part_df = part_df = df[['word', 'translate']]
                    else:
                        part_df = df.loc[df['repit'] == 0]['word', 'translate'].sample(n=5)

                    for index, row in part_df.iterrows():
                        word = row['word']
                        translate = row['translate']
                        mask = (df['word'] == word) & (df['translate'] == translate)
                        df.loc[mask, 'repit'] = 1

                    part_df['rating'] = 2
                    part_df['repit'] = 0
                    part_df['count_errors'] = 0

                word, options = generate_question(part_df)
                print(word, options)
                markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
                for option in options:
                    markup.add(telebot.types.KeyboardButton(option))
                start_time = time.perf_counter()
                bot.send_message(message.chat.id, f"Який переклад слова '{word}'?", reply_markup=markup)
            if value_mean != 0 and (df['repit'] == 0).sum() == 0 and part_df.shape[0] != 0:
                word, options = generate_question(part_df)
                print(word, options)
                markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
                for option in options:
                    markup.add(telebot.types.KeyboardButton(option))
                start_time = time.perf_counter()
                bot.send_message(message.chat.id, f"Який переклад слова '{word}'?", reply_markup=markup)

    elif message.text == 'Загрузить файл слів' or message.text == 'Загрузить новий файл слів':
        file_s = 1
        bot.send_message(message.from_user.id, 'Надішли мені файл  .csv або .txt із словами, які хочеш вивчати.У якому перший рядок це назви колонок - word,translate. І у кожному новому рядку має бути записано слово та переклад через кому. Наприклад: \nword,translate\n hello,привіт\n Ukraine,Україна ', parse_mode='Markdown')
    elif message.text == 'Додати слова до наявного файлу' :
        file_s = 2
        bot.send_message(message.from_user.id, 'Надішли мені файл  .csv або .txt із словами, які хочеш додати до наявного файлу для вичення.У якому перший рядок це назви колонок - word,translate. І у кожному новому рядку має бути записано слово та переклад через кому. Наприклад: \nword,translate\n hello,привіт\n Ukraine,Україна ', parse_mode='Markdown')
    elif message.text == 'Повторити складні для мене слова':
        df.loc[df['count_errors'] > (df['repit'].mean() - df['repit'].std()), 'repit'] = 0
        part_df = pd.DataFrame()
        if df.loc[df['repit'] == 0].shape[0] <= 5:
            part_df = df.loc[df['repit'] == 0][['word', 'translate']].sample(n=df.loc[df['repit'] == 0].shape[0])
        else:
            part_df = df.loc[df['repit'] == 0]['word', 'translate'].sample(n=5)
        for index, row in part_df.iterrows():
            word = row['word']
            translate = row['translate']
            mask = (df['word'] == word) & (df['translate'] == translate)
            df.loc[mask, 'repit'] = 1
        part_df['rating'] = 2
        part_df['repit'] = 0
        part_df['count_errors'] = 0

        word, options = generate_question(part_df)
        print(word, options)
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
        for option in options:
            markup.add(telebot.types.KeyboardButton(option))
        start_time = time.perf_counter()
        bot.send_message(message.chat.id, f"Який переклад слова '{word}'?", reply_markup=markup)


bot.polling(none_stop=True, interval=0)