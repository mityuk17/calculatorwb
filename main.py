import datetime
import geopy.distance
import re
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import config


logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot, storage=storage)


class States(StatesGroup):
    get_sale_price = State()
    get_tax_rate = State()
    get_fulfillment_price = State()
    get_intermediary_percentage = State()
    get_commission_percentage = State()
    get_delivery_fee = State()
    get_redemption_percentage = State()
    get_supplier_cost = State()
    get_dollar_exchange_rate = State()
    get_item_weight = State()
    get_china_logistics_price = State()


def check_digit(dig):
    reg_exp = r'\d+(\.\d+)?'
    if re.fullmatch(reg_exp, dig):
        return True
    else:
        return False

def calculate_total_cost(sale_price, tax_rate, fulfillment_price, intermediary_percentage,
                         commission_percentage, delivery_fee, redemption_percentage, supplier_cost,
                         dollar_exchange_rate, item_weight, chia_logistics_price):
    total_cost = sale_price-(((10*delivery_fee+33*((100-redemption_percentage)/10)/10)+(sale_price*tax_rate/100)+fulfillment_price+supplier_cost+(supplier_cost*intermediary_percentage/100)+(sale_price*commission_percentage/100)+(item_weight*dollar_exchange_rate*chia_logistics_price)))
    return total_cost


async def check_subscribe(user_id):
    member_status = await bot.get_chat_member(chat_id=config.channel_id, user_id=user_id)
    if isinstance(member_status, types.ChatMemberLeft):
        return False
    else:
        return True


@dp.message_handler(commands = ['start'], state='*')
async def start(message: types.Message):
    check = await check_subscribe(message.chat.id)
    if not check:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Подписаться', url=config.channel_link))
        kb.add(types.InlineKeyboardButton(text='Проверить подписку', callback_data='check_subscription'))
        await message.answer(f'Для работы с ботом необходимо подписаться на канал: {config.channel_link}', reply_markup=kb)
        return
    await message.answer('''Пришлите цены продажи на маркетплейсе:''')
    await States.get_sale_price.set()


@dp.callback_query_handler(lambda query: query.data == 'check_subscription', state='*')
async def check_subscription(callback_query: types.CallbackQuery):
    check = await check_subscribe(callback_query.from_user.id)
    if not check:
        await callback_query.answer('Вы не подписаны на канал.')
        return
    await callback_query.message.delete()
    await callback_query.message.answer('''Пришлите цены продажи на маркетплейсе:''')
    await States.get_sale_price.set()

@dp.message_handler(state= States.get_sale_price)
async def get_item1(message: types.Message, state: FSMContext):
    if not check_digit(message.text):
        await message.answer('''Неверный формат''')
        return
    async with state.proxy() as data:
        data['sale_price'] = float(message.text)
    await States.get_tax_rate.set()
    await message.answer('Пришлите налог')


@dp.message_handler(state=States.get_tax_rate)
async def get_item2(message: types.Message, state: FSMContext):
    if not check_digit(message.text):
        await message.answer('''Неверный формат.''')
        return
    async with state.proxy() as data:
        data['tax_rate'] = float(message.text)
    await States.get_fulfillment_price.set()
    await message.answer('Пришлите цену фулфилмент:')



@dp.message_handler(state=States.get_fulfillment_price)
async def get_item2(message: types.Message, state: FSMContext):
    if not check_digit(message.text):
        await message.answer('''Неверный формат.''')
        return
    async with state.proxy() as data:
        data['fulfillment_price'] = float(message.text)
    await States.get_intermediary_percentage.set()
    await message.answer('Пришлите процент посредника:')


@dp.message_handler(state=States.get_intermediary_percentage)
async def get_item2(message: types.Message, state: FSMContext):
    if not check_digit(message.text):
        await message.answer('''Неверный формат.''')
        return
    async with state.proxy() as data:
        data['intermediary_percentage'] = float(message.text)
    await States.get_commission_percentage.set()
    await message.answer('Пришлите процент маркетплейса:')


@dp.message_handler(state=States.get_commission_percentage)
async def get_item2(message: types.Message, state: FSMContext):
    if not check_digit(message.text):
        await message.answer('''Неверный формат.''')
        return
    async with state.proxy() as data:
        data['commission_percentage'] = float(message.text)
    await States.get_delivery_fee.set()
    await message.answer('Пришлите цену доставки маркетплейса:')

@dp.message_handler(state=States.get_delivery_fee)
async def get_item2(message: types.Message, state: FSMContext):
    if not check_digit(message.text):
        await message.answer('''Неверный формат.''')
        return
    async with state.proxy() as data:
        data['delivery_fee'] = float(message.text)
    await States.get_redemption_percentage.set()
    await message.answer('Пришлите процент выкупа:')


@dp.message_handler(state=States.get_redemption_percentage)
async def get_item2(message: types.Message, state: FSMContext):
    if not check_digit(message.text):
        await message.answer('''Неверный формат.''')
        return
    async with state.proxy() as data:
        data['redemption_percentage'] = float(message.text)
    await States.get_supplier_cost.set()
    await message.answer('Пришлите цену поставщика:')


@dp.message_handler(state=States.get_supplier_cost)
async def get_item2(message: types.Message, state: FSMContext):
    if not check_digit(message.text):
        await message.answer('''Неверный формат.''')
        return
    async with state.proxy() as data:
        data['supplier_cost'] = float(message.text)
    await States.get_dollar_exchange_rate.set()
    await message.answer('Пришлите курс доллара (руб):')


@dp.message_handler(state=States.get_dollar_exchange_rate)
async def get_item2(message: types.Message, state: FSMContext):
    if not check_digit(message.text):
        await message.answer('''Неверный формат.''')
        return
    async with state.proxy() as data:
        data['dollar_exchange_rate'] = float(message.text)
    await States.get_item_weight.set()
    await message.answer('Пришлите вес товара (кг):')


@dp.message_handler(state=States.get_item_weight)
async def get_item2(message: types.Message, state: FSMContext):
    if not check_digit(message.text):
        await message.answer('''Неверный формат.''')
        return
    async with state.proxy() as data:
        data['item_weight'] = float(message.text)
    await States.get_china_logistics_price.set()
    await message.answer('Пришлите тариф доставки из Китая ($/кг):')


@dp.message_handler(state=States.get_china_logistics_price)
async def get_all_data(message: types.Message, state: FSMContext):
    if not check_digit(message.text):
        await message.answer('''Неверный формат.''')
        return
    async with state.proxy() as data:
        sale_price = data['sale_price']
        tax_rate = data['tax_rate']
        fulfillment_price = data['fulfillment_price']
        intermediary_percentage = data['intermediary_percentage']
        commission_percentage = data['commission_percentage']
        delivery_fee = data['delivery_fee']
        redemption_percentage = data['redemption_percentage']
        supplier_cost = data['supplier_cost']
        dollar_exchange_rate = data['dollar_exchange_rate']
        item_weight = data['item_weight']
        china_logistics_price = float(message.text)
    total_cost = calculate_total_cost(sale_price, tax_rate, fulfillment_price, intermediary_percentage, commission_percentage, delivery_fee, redemption_percentage, supplier_cost, dollar_exchange_rate, item_weight, china_logistics_price)
    total_cost_percent = (total_cost/sale_price)*100
    await message.answer(f'Маржа в рублях: {total_cost}')
    await message.answer(f'Маржа в %: {total_cost_percent}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)