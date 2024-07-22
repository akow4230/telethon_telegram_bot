from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loader import dp, db, bot
from telethon.sync import TelegramClient

group_n = 0
user_id = 0

@dp.message_handler(commands=['msg'])
async def start(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    web_app_button1 = types.InlineKeyboardButton(text='Group 1', callback_data='group1')
    web_app_button2 = types.InlineKeyboardButton(text='Group 2', callback_data='group2')
    web_app_button3 = types.InlineKeyboardButton(text='Group 3', callback_data='group3')
    web_app_button4 = types.InlineKeyboardButton(text='Group 4', callback_data='group4')
    markup.add(web_app_button1, web_app_button2)
    markup.add(web_app_button3, web_app_button4)
    await message.reply("Please select the group:", reply_markup=markup)

@dp.callback_query_handler(lambda query: query.data.startswith('group') or query.data.startswith('act'))
async def process_callback(callback_query: types.CallbackQuery):
    global group_n, user_id

    button_data = callback_query.data
    if button_data.startswith('group'):
        group_number = button_data[5:]
        group_n = int(group_number)
        await callback_query.message.delete()
        accounts = await db.select_all_accounts()
        markup = types.InlineKeyboardMarkup()
        for account in accounts:
            account_button = types.InlineKeyboardButton(
                text=f"Account {account['full_name']}",
                callback_data=f"act{account['telegram_id']}"
            )
            markup.add(account_button)
        await callback_query.message.answer("Please select an account:", reply_markup=markup)
    elif button_data.startswith('act'):
        telegram_id = button_data[3:]
        user_id = int(telegram_id)
        await callback_query.message.delete()
        await callback_query.message.answer("Please send text:")
        await TextInput.waiting_for_text.set()



class TextInput(StatesGroup):
    waiting_for_text = State()




async def send_telegram_message(api_id, api_hash, group, message_text, fayl):
    async with TelegramClient(fayl, api_id, api_hash) as client:
        try:
            user_entity = await client.get_entity(group)
            await client.send_message(user_entity, message_text)
            print("Message sent successfully!")
            me = await client.get_me()
            print(f"Logged in as: {me.first_name}")


        except ValueError as e:
            print(f"Error: {e}")

@dp.message_handler(state=TextInput.waiting_for_text)
async def save_text(message: types.Message, state: FSMContext):
    global group_n, user_id
    print(user_id)
    account_details = await db.select_account(user_id)
    if account_details:
        api_id = account_details['api_id']
        api_hash = account_details['api_hash']
        fayl = account_details['session']
        if group_n == 1:
            await send_telegram_message(api_id, api_hash, "https://t.me/group1telethon", message.text, fayl)
        elif group_n == 2:
            await send_telegram_message(api_id, api_hash, "https://t.me/group2telethon", message.text, fayl)
        elif group_n == 3:
            await send_telegram_message(api_id, api_hash, "https://t.me/group3telethon", message.text, fayl)
        elif group_n == 4:
            await send_telegram_message(api_id, api_hash, "https://t.me/group4telethon", message.text, fayl)
        else:
            await message.answer("Something went wrong!")

        await message.answer("Message sent successfully!")
    else:
        await message.answer("Account details not found!")

    group_n = 0
    user_id = 0
    await state.finish()
