from aiogram import types, Router, Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder 
import config
import states
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest, TelegramForbiddenError
from aiogram.utils.media_group import MediaGroupBuilder
from datetime import datetime, timedelta
from bd import BDRequests
import os
import sys
from aiogram.fsm.strategy import FSMStrategy

bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.MARKDOWN_V2)
dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
router = Router()
BD = BDRequests()

#Отображение приветсвеного меню
async def main_menu(msg):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="✅ Разместить объявление" , callback_data=f"create_news"))
    keyboard = builder.as_markup(resize_keyboard=True)
    #Ссылка на приветсвенное фото
    photo = "https://gas-kvas.com/grafic/uploads/posts/2023-10/1696502289_gas-kvas-com-p-kartinki-lyubie-45.jpg"
    #Приветсвенный текст
    text = 'Привет! В этом боте вы сможете разместить объявления в канале "" @123\n\nНажмите на кнопку "✅ Разместить объявление" 👇'
    #Если попали через команду /start
    if type(msg) is Message:
        await msg.answer_photo(photo, caption=text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    #Если через кнопку
    elif type(msg) is types.CallbackQuery:
        await msg.message.answer_photo(photo, caption=text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    

#Запуск бота
@router.message(Command("start"))
async def cmd_start(msg: Message):
    #Если не в канале для администраторов
    if str(msg.chat.id) not in config.ADMINS_CHANNEL:
        await main_menu(msg)
    else:
        builder = ReplyKeyboardBuilder()
        builder.row(types.KeyboardButton(text='/all_news', callback_data='all_news'), types.KeyboardButton(text='/stat', callback_data='stat'), types.KeyboardButton(text='/restart', callback_data='restart'))
        keyboard = builder.as_markup(resize_keyboard=True)
        await msg.answer("Добро пожаловать в панель администратора:\nКоманды:\n/all_news - Отображение всех предложенных новостей\n/restart - Перезапуск всего бота\n/stat - Текущее состояение бота, если не отвечает перезапустить", reply_markup=keyboard, parse_mode=ParseMode.HTML)

#Если отвечает на команду значит работает
@router.message(Command("stat"))
async def cmd_stat(msg: Message):
    await msg.answer("Бот работает")

#Отображение всех заявок
@router.message(Command("all_news"))
async def all_news(msg: Message):
    all_data = BD.select_all()
    #Eckb нет записей
    if len(all_data) == 0:
        await msg.answer("Нету предложенных записей")
        return
    for data in all_data:
        #Если есть картинки
        if len(data[2]) != 0:
            media_group = MediaGroupBuilder(caption=data[1])
            for image_id in data[2]:
                media_group.add_photo(type="photo", media=image_id)
            await bot.send_media_group(config.ADMINS_CHANNEL, media=media_group.build())
        else:
            await bot.send_message(config.ADMINS_CHANNEL, data[1])
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="✅ Да" , callback_data=f"Accepted:ID:{data[0]}"))
        builder.add(types.InlineKeyboardButton(text="❌ Нет" , callback_data=f"Not_accepted:ID:{data[0]}"))
        keyboard = builder.as_markup(resize_keyboard=True)
        await bot.send_message(config.ADMINS_CHANNEL, "Опубликовать?", reply_markup=keyboard)

#Перезапуск
@router.message(Command("restart"))
async def restart(msg: Message):
    #Доступен только в канале администраторов
    if str(msg.chat.id) in config.ADMINS_CHANNEL:
        await msg.answer("Перезапуск бота\.\.\.\n")
        python = sys.executable
        os.execl(python, python, *sys.argv)
    else:
        await msg.answer("Недостаточно прав\n")

#Если админ принял пост
@router.callback_query(lambda c: 'Accepted' in c.data)
async def accept_post(callback_query: types.CallbackQuery):
    id = callback_query.data.split(":")[2]
    data = BD.select_by_id(id)
    if len(data) != 3:
        return
    #Если есть картинки
    if len(data[2]) != 0:
        media_group = MediaGroupBuilder(caption=data[1])
        for image_id in data[2]:
            media_group.add_photo(type="photo", media=image_id)
        await bot.send_media_group(config.CHANELL_ID, media=media_group.build())
    else:
        await bot.send_message(config.CHANELL_ID, data[1])
    BD.delete_by_id(id)
    await callback_query.message.answer("Новость опубликована")

#Если админ не принял пост
@router.callback_query(lambda c: 'Not_accepted' in c.data)
async def reject_post(callback_query: types.CallbackQuery):
    id = callback_query.data.split(":")[2]
    data = BD.select_by_id(id)
    if len(data) != 3:
        return
    BD.delete_by_id(id)
    await callback_query.message.answer("Новость удалена")

#Обработка кнопки назад, т.е выход на главный экран
@router.callback_query(lambda c: c.data == 'Назад')   
async def exit(callback_query: types.CallbackQuery, state: FSMContext):     
    await state.clear()
    await main_menu(callback_query)

#Обработка цепочки создания новости
@router.callback_query(lambda c: c.data == 'create_news')
async def cmd_create_news(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(states.CreateNews.text)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Вперед', callback_data='Вперед'), types.InlineKeyboardButton(text='Назад', callback_data='Назад'))
    builder.adjust(1) 
    keyboard = builder.as_markup(resize_keyboard=True)
    await callback_query.message.answer("Введите текст своего объявления\.", reply_markup=keyboard)

#Экранирование специальных символов
def escape_markdown(text):
    special_characters = '\\`*_{}[]()#+-.!~><=|'
    for char in special_characters:
        text = text.replace(char, '\\' + char)
    return text

#Обработка введенного текста
@router.message(states.CreateNews.text, F.text)
async def get_text(msg: Message, state: FSMContext):
    text = escape_markdown(msg.text)
    await state.update_data(text=text)

#Обработка кнопки Вперед
@router.callback_query(states.CreateNews.text)
async def get_next(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(states.CreateNews.images)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Вперед', callback_data='Вперед'), types.InlineKeyboardButton(text='Назад', callback_data='Назад'))
    builder.adjust(1) 
    keyboard = builder.as_markup(resize_keyboard=True)
    await callback_query.message.answer('Прикрепите одно или несколько фото, либо нажмите "Вперед" чтобы пропустить этот шаг\.', reply_markup=keyboard)

#Обработка полученных изображений игнорирует сообщения не являющиеся фотографиями
@router.message(states.CreateNews.images, F.photo)
async def get_image(msg: Message, state: FSMContext):
    data = await state.get_data()
    #Добавление к существующим если уже есть
    if 'images' in data.keys():
        image = data['images']
        image.append(msg.photo[0].file_id)
        await state.update_data(images=image)
    else:
        await state.update_data(images=[msg.photo[0].file_id])
    return

#Обработка кнопки Вперед и формирование превью 
@router.callback_query(states.CreateNews.images)
async def get_next(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(states.CreateNews.result)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="✅ Да" , callback_data=f"send_news"))
    builder.add(types.InlineKeyboardButton(text="❌ Нет" , callback_data=f"Назад"))
    keyboard = builder.as_markup(resize_keyboard=True)
  
    data = await state.get_data()
    #Получение текста
    if 'text' in data.keys():
        text = data['text']
    else:
        text = ""

    #Если есть фото
    if 'images' in data.keys():
        image_ids = data['images'] 
        media_group = MediaGroupBuilder(caption=text)
        for image_id in image_ids:
            media_group.add_photo(type="photo", media=image_id)
        await callback_query.message.answer_media_group(media=media_group.build())
    #Если нет ни фото ни текста
    elif text == "":
        await callback_query.message.answer("Должен быть заполнен хотя бы один пункт")
        await exit(callback_query, state)
        return
    #Если только текст
    else:
        await callback_query.message.answer(text)
    await callback_query.message.answer("Опубликовать?", reply_markup=keyboard)



#Формирование поста и отправка результата в канал админов
@router.callback_query(states.CreateNews.result)
async def get_result(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    #Получение текста
    if 'text' in data.keys():
        text = data['text']
    else:
        text = ""
    #Добавление имени пользователя
    username = callback_query.from_user.full_name
    if len(username) < 4:
        username = "Посмотреть профиль пользователя" 
    text += f"\n\n📲tg: [{username}]({callback_query.from_user.url})"
    
    #Добавление футера
    if config.FOOTER_TEXT != "off":
        if config.FOOTER_LINK == "off":
            text += "\n\n" + config.FOOTER_TEXT
        else:
            text += f"\n\n[{config.FOOTER_TEXT}]({config.FOOTER_LINK})"
    
    #Обработка изображений
    image_ids = []
    if 'images' in data.keys():
        image_ids = data['images'] 
        media_group = MediaGroupBuilder(caption=text)
        for image_id in image_ids:
            media_group.add_photo(type="photo", media=image_id)
        await bot.send_media_group(config.ADMINS_CHANNEL, media=media_group.build())
    else:
        await bot.send_message(config.ADMINS_CHANNEL, text)
    id = BD.insert_news(text, image_ids)

    #Отправка в канал админов результата
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="✅ Да" , callback_data=f"Accepted:ID:{id}"))
    builder.add(types.InlineKeyboardButton(text="❌ Нет" , callback_data=f"Not_accepted:ID:{id}"))
    keyboard = builder.as_markup(resize_keyboard=True)
    await bot.send_message(config.ADMINS_CHANNEL, "Опубликовать?", reply_markup=keyboard)
    
    #Ответ пользователю и выход на главный экран
    await state.clear()
    await callback_query.message.answer('Скоро ваше объявление будут опубликовано в канале\.')
    await main_menu(callback_query)

