from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *

api = "7321733071:AAGznzOU5RCy6j1tEJ3vbhGRYeIj1Xygqqw"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())
kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb2 = InlineKeyboardMarkup(resize_keyboard=True)
button1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button2 = InlineKeyboardButton(text='Формулы рассчёта', callback_data='formulas')
button_start = KeyboardButton(text='Рассчитать')
button_info = KeyboardButton(text='Информация')
button_buy = KeyboardButton(text = "Купить")
button_register = KeyboardButton(text="Регистрация")
buy_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Product1", callback_data="product_buying")],
        [InlineKeyboardButton(text="Product2", callback_data="product_buying")],
        [InlineKeyboardButton(text="Product3", callback_data="product_buying")],
        [InlineKeyboardButton(text="Product4", callback_data="product_buying")]
    ]
)
kb.insert(button_start)
kb.insert(button_info)
kb.add(button_buy)
kb2.insert(button1)
kb2.insert(button2)
kb.insert(button_register)



products_data = get_all_products()
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью", reply_markup=kb)


@dp.message_handler(text="Рассчитать")
async def main_menu(message):
    await message.answer("Выберите опцию:", reply_markup=kb2)

@dp.message_handler(text="Купить")
async def get_buying_list(message):
    for num in range(1, 5):
        with open(f"pictures/{num}.jpg", "rb") as img:
            await message.answer_photo(img, f"Название: {products_data[num - 1][1]} | Описание: "
                                            f"{products_data[num - 1][2]} | Цена: {products_data[num - 1][3]}")
        img.close()
    await message.answer("Выберите продукт для покупки:", reply_markup=buy_kb)

@dp.callback_query_handler(text="product_buying")
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer(
        f"для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5\n для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161")
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст: ')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=float(message.text))
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=float(message.text))
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=float(message.text))
    data = await state.get_data()
    await message.answer(
        f"Ваша норма калорий: {round(10 * data['weight'] + 6.25 * data['growth'] - 5 * data['age'] + 5, 2)}")
    await state.finish()


@dp.message_handler(text='Информация')
async def information(message):
    await message.answer("Это бот для расчёта калорий")


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State(F"{1000}")

@dp.message_handler(text="Регистрация")
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит)")

    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    initiate_db()
    data = await state.get_data()
    user_in_table = cursor.execute("SELECT username FROM Users").fetchall()
    if RegistrationState.username not in user_in_table:
        RegistrationState.username = message.text
        await message.answer("Введите свой email:")
        await state.update_data(email=message.text)
        RegistrationState.email = message.text
    else:
        await message.answer("Пользователь существует, введите другое имя")
        await state.update_data(username=message.text)

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    RegistrationState.email = message.text
    await message.answer("Введите свой возраст:")
    await state.update_data(age=message.text)

@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    RegistrationState.age = message.text
    add_user(RegistrationState.username, RegistrationState.email, RegistrationState.age)
    await state.finish()
    connection.close()

@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
