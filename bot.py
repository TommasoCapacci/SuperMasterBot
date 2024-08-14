import random
import telebot
from telebot import types

from constants import API_KEY

## Variables

bot = telebot.TeleBot(API_KEY)
games = dict()


## Support functions

def generate_random_code(length):
    return [random.randint(0, 9) for _ in range(length)]

def compute_matches(code, guess):
    perfect_matches = 0
    filtered_code = []
    filtered_guess = []
    for i in range(len(code)):
        if code[i]==guess[i]:
            perfect_matches += 1
        else:
            filtered_code.append(code[i])
            filtered_guess.append(guess[i])
    out_of_order = 0
    for g in filtered_guess:
        if g in filtered_code:
            out_of_order += 1
            filtered_code.remove(g)
    return perfect_matches, out_of_order


### Commands

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    easy_btn = types.InlineKeyboardButton('Easy (4 digits code)', callback_data='4')
    med_btn = types.InlineKeyboardButton('Medium (5 digits)', callback_data='5')
    hard_btn = types.InlineKeyboardButton('Hard (6 digits)', callback_data='6')
    markup.add(easy_btn, med_btn, hard_btn)
    bot.send_message(message.chat.id, 'Hello! Select the difficulty for your next game:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def create_game(callback):
    global games

    if callback.message:
        user_id = callback.message.chat.id
        code_length = int(callback.data)
        code = generate_random_code(code_length)
        games[user_id] = code
        print(f'New game for user {user_id} -> code: {code}')
        bot.send_message(callback.message.chat.id, 'New game created. You can start breaking the code using the "guess" command. Have fun!')

@bot.message_handler(commands=['guess'])
def guess(message):
    global games

    code = games.get(message.chat.id, None)
    if code is None:
        bot.reply_to(message, 'No valid game for this user was found. Please use the "/start" command to create a new game.')
    else:
        arguments = message.text.split()
        if len(arguments) < 2:
            bot.reply_to(message, 'Invalid use of the "guess" command: please send the command followed by your guess (guess XXX...X).')
        elif len(arguments[1]) != len(code):
            bot.reply_to(message, f'Length of guessed code does not match with the provided one.\nCorrect length: {len(code)}')
        else:
            guessed_code = [int(c) for c in arguments[1]]
            p, o = compute_matches(code, guessed_code)
            if p == len(code):
                response = 'Code guessed, congratulations!\n\nUse the "/start" commad to create a new game.'
                del games[message.chat.id]
            else:
                response = f'Perfect matches: {p}\nOut of order: {o}'
            bot.reply_to(message, response)


### Main

if __name__ == '__main__':
    print("Starting polling...")
    bot.polling()