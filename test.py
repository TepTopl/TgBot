import telebot

# Токен от BotFather
TOKEN = '7363821822:AAH0lx8RuWYY6pmA1WN0jSNcKtCP69NmIHQ'
bot = telebot.TeleBot(TOKEN)

# Состояния пользователей
user_state = {}
user_data = {}  # Храним все коэффициенты

# Таблица КВС: [Возраст][Стаж] → коэффициент
KVS_TABLE = {
    '16-21':     [2.27, 1.92, 1.84, 1.65, 1.62, None, None, None],
    '22-24':     [1.88, 1.72, 1.71, 1.13, 1.10, 1.09, None, None],
    '25-29':     [1.72, 1.60, 1.54, 1.09, 1.08, 1.07, 1.02, None],
    '30-34':     [1.56, 1.50, 1.48, 1.05, 1.04, 1.01, 0.97, 0.95],
    '35-39':     [1.54, 1.47, 1.46, 1.00, 0.97, 0.95, 0.94, 0.93],
    '40-49':     [1.50, 1.44, 1.43, 0.96, 0.95, 0.94, 0.93, 0.91],
    '50-59':     [1.46, 1.40, 1.39, 0.93, 0.92, 0.91, 0.90, 0.86],
    '59+':       [1.43, 1.36, 1.35, 0.91, 0.90, 0.89, 0.88, 0.83]
}

# КТ — коэффициент территории
KT = {
    'севастополь': 1.65,
    'симферополь': 1.55,
    'иные города крыма': 1.54
}

# КБМ — коэффициент бонус-малус
KBM = {
    '0': 1.76,
    '1': 1.17,
    '2': 1.0,
    '3': 0.91,
    '4': 0.83,
    '5': 0.78,
    '6': 0.74,
    '7': 0.68,
    '8': 0.63,
    '9': 0.57,
    '10': 0.52,
    '11': 0.46
}

# КО — коэффициент ограничения
KO = {
    'мультидрайв': 2.32,
    'ограниченное количество': 1.0
}

# КМ — коэффициент мощности
KM = {
    'до 50 л.с.': 0.6,
    '51 - 70 л.с.': 1.0,
    '71 - 100 л.с.': 1.1,
    '101 - 120 л.с.': 1.2,
    '121 - 150 л.с.': 1.4,
    'свыше 150': 1.6
}

# КС — коэффициент числа мест
KS = {
    '3': 0.5,
    '4': 0.6,
    '5': 0.65,
    '6': 0.7,
    '7': 0.8,
    '8': 0.9,
    '9': 0.95,
    '10+': 1.0
}

# Функция определения возрастной группы
def get_age_group(age):
    if 16 <= age <= 21:
        return '16-21'
    elif 22 <= age <= 24:
        return '22-24'
    elif 25 <= age <= 29:
        return '25-29'
    elif 30 <= age <= 34:
        return '30-34'
    elif 35 <= age <= 39:
        return '35-39'
    elif 40 <= age <= 49:
        return '40-49'
    elif 50 <= age <= 59:
        return '50-59'
    elif age >= 60:
        return '59+'
    else:
        return None

# Функция определения группы стажа (возвращает индекс)
def get_stazh_index(stazh):
    if stazh == 0: return 0
    elif stazh == 1: return 1
    elif stazh == 2: return 2
    elif 3 <= stazh <= 4: return 3
    elif 5 <= stazh <= 6: return 4
    elif 7 <= stazh <= 9: return 5
    elif 10 <= stazh <= 14: return 6
    elif stazh >= 15: return 7
    else: return None

# Обработчик /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_state[user_id] = 'waiting_for_age_stazh'
    user_data[user_id] = {}
    bot.reply_to(message, "Привет! Введите ваш лет и стаж вождения через пробел.\nНапример: 34 5")

# Основной обработчик
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text.strip().lower()  # приводим к нижнему регистру

    # Если пользователь новый — начнём сначала
    if user_id not in user_state:
        user_state[user_id] = 'waiting_for_age_stazh'
        user_data[user_id] = {}

    state = user_state[user_id]

    try:
        # Шаг 1: Ввод возраста и стажа
        if state == 'waiting_for_age_stazh':
            parts = text.split()
            if len(parts) != 2:
                bot.reply_to(message, "Введите два числа: возраст и стаж (например: 34 5)")
                return
            age = int(parts[0])
            stazh = int(parts[1])

            if age < 16:
                bot.reply_to(message, "Возраст должен быть не менее 16 лет.")
                return
            if stazh < 0:
                bot.reply_to(message, "Стаж не может быть отрицательным.")
                return

            age_group = get_age_group(age)
            stazh_idx = get_stazh_index(stazh)

            if not age_group:
                bot.reply_to(message, "Возраст вне допустимого диапазона.")
                return
            if stazh_idx is None:
                bot.reply_to(message, "Некорректный стаж.")
                return

            kvs_row = KVS_TABLE[age_group]
            if stazh_idx >= len(kvs_row) or kvs_row[stazh_idx] is None:
                bot.reply_to(message, f"Для группы {age_group} и стажа {stazh} данных нет.")
                return

            kvs_value = kvs_row[stazh_idx]
            user_data[user_id]['KVS'] = kvs_value
            user_state[user_id] = 'waiting_for_city'

            bot.reply_to(message, f"✅ КВС: {kvs_value:.2f}")
            bot.reply_to(message, "Введите ваш город: Севастополь, Симферополь или Иные города Крыма")

        # Шаг 2: Город → КТ
        elif state == 'waiting_for_city':
            city_key = text.replace(' ', '').lower()
            if 'севастополь' in city_key:
                kt_value = KT['севастополь']
            elif 'симферополь' in city_key:
                kt_value = KT['симферополь']
            elif 'иные' in city_key or 'другие' in city_key or 'крым' in city_key:
                kt_value = KT['иные города крыма']
            else:
                bot.reply_to(message, "Пожалуйста, введите: Севастополь, Симферополь или Иные города Крыма")
                return

            user_data[user_id]['KT'] = kt_value
            user_state[user_id] = 'waiting_for_kbm'

            bot.reply_to(message, f"✅ КТ: {kt_value}")
            bot.reply_to(message, "Введите ваш безаварийный стаж вождения, если свыше 11 лет ставьте значение 11 (КБМ): от 0 до 11 (например: 3)")

        # Шаг 3: КБМ
        elif state == 'waiting_for_kbm':
            if text in KBM:
                kbm_value = KBM[text]
                user_data[user_id]['KBM'] = kbm_value
                user_state[user_id] = 'waiting_for_ko'
                bot.reply_to(message, f"✅ КБМ: {kbm_value}")
                bot.reply_to(message, "Выберите тип управления:\n- мультидрайв\n- ограниченное количество")
            else:
                bot.reply_to(message, "Введите число от 0 до 11 (например: 3)")

        # Шаг 4: КО (тип управления)
        elif state == 'waiting_for_ko':
            if text == 'мультидрайв':
                ko_value = KO['мультидрайв']
            elif text == 'ограниченное количество':
                ko_value = KO['ограниченное количество']
            else:
                bot.reply_to(message, "Выберите: мультидрайв или ограниченное количество")
                return

            user_data[user_id]['KO'] = ko_value
            user_state[user_id] = 'waiting_for_km'

            bot.reply_to(message, f"✅ КО: {ko_value}")
            bot.reply_to(message, "Выберите мощность двигателя:\n"
                                  "до 50 л.с.\n"
                                  "51 - 70 л.с.\n"
                                  "71 - 100 л.с.\n"
                                  "101 - 120 л.с.\n"
                                  "121 - 150 л.с.\n"
                                  "свыше 150")

        # Шаг 5: КМ (мощность)
        elif state == 'waiting_for_km':
            km_key = None
            if 'до 50' in text:
                km_key = 'до 50 л.с.'
            elif '51' in text or '70' in text:
                km_key = '51 - 70 л.с.'
            elif '71' in text or '100' in text:
                km_key = '71 - 100 л.с.'
            elif '101' in text or '120' in text:
                km_key = '101 - 120 л.с.'
            elif '121' in text or '150' in text:
                km_key = '121 - 150 л.с.'
            elif 'свыше' in text or '150+' in text:
                km_key = 'свыше 150'

            if km_key and km_key in KM:
                user_data[user_id]['KM'] = KM[km_key]
                user_state[user_id] = 'waiting_for_ks'
                bot.reply_to(message, f"✅ КМ: {KM[km_key]}")
                bot.reply_to(message, "Введите количество мест в авто: 3, 4, 5, 6, 7, 8, 9, 10+")
            else:
                bot.reply_to(message, "Выберите один из вариантов мощности.")

        # Шаг 6: КС (число мест)
        elif state == 'waiting_for_ks':
            if text in KS:
                ks_value = KS[text]
                user_data[user_id]['KS'] = ks_value
                user_state[user_id] = 'finished'

                # Все данные собраны — считаем стоимость
                data = user_data[user_id]
                base = 7200
                total = data['KBM'] * data['KVS'] * data['KM'] * data['KO'] * data['KT'] * data['KS'] * base

                bot.reply_to(message, f"✅ Все данные получены!\n\n"
                                      f"КВС: {data['KVS']:.2f}\n"
                                      f"КТ: {data['KT']}\n"
                                      f"КБМ: {data['KBM']}\n"
                                      f"КО: {data['KO']}\n"
                                      f"КМ: {data['KM']}\n"
                                      f"КС: {data['KS']}\n\n"
                                      f"💰 Итоговая стоимость полиса: {total:,.2f} ₽")

                # Спрашиваем, начать заново?
                bot.reply_to(message, "Чтобы начать заново, введите /start")

            else:
                bot.reply_to(message, "Введите корректное количество мест: 3, 4, 5, ..., 10+")

    except Exception as e:
        bot.reply_to(message, "Ошибка ввода. Попробуйте снова.")
        print(f"Error: {e}")

# Запуск бота
print("Бот запущен...")
bot.polling(none_stop=True)