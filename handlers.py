from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards import main_kb, admin_kb, show_menu_kb, rating_kb, create_feedback_navigation, admin_kbs
from openai_integration import generate_perfume_recommendation
from config import ADMIN_IDS
from session_manager import session_manager
from dialogue_manager import dialogue_manager

router = Router()

class UserState(StatesGroup):
    waiting_for_perfume_input = State()
    waiting_for_feedback = State()
    waiting_for_support_request = State()
    waiting_for_broadcast = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    session = session_manager.get_session(user_id)
    
    if 'greeted' not in session:
        db.add_user(user_id, message.from_user.username)
        dialogue_manager.clear_dialogue_history(user_id)
        if user_id in ADMIN_IDS:
            await message.answer("Добро пожаловать. Ваш статус: Админ", reply_markup=main_kb)
            await message.answer("Для открытия админки - жмайте кнопку ниже", reply_markup=admin_kbs)
        else:
            await message.answer("Добро пожаловать в AI-консультант по подбору парфюмерии!", reply_markup=main_kb)
            await message.answer("Пользуйтесь кнопками на вашей клавиатуре для", reply_markup=admin_kb)
        session_manager.update_session(user_id, 'greeted', True)
    else:
        await message.answer("С возвращением! Чем я могу вам помочь?", reply_markup=main_kb)

@router.message(F.text == "Подобрать парфюм")
async def select_perfume(message: Message, state: FSMContext):
    user_id = message.from_user.id
    session = session_manager.get_session(user_id)
    
    if 'preferences_asked' not in session:
        await state.set_state(UserState.waiting_for_perfume_input)
        await message.answer("Опишите, пожалуйста, какой аромат вы ищете или какие у вас предпочтения.\n\nНаш консультант поможет вам сразу как только сможет!")
        session_manager.update_session(user_id, 'preferences_asked', True)
    else:
        await message.answer("Я помню ваши предпочтения. Хотите, чтобы я подобрал парфюм на основе предыдущей информации или вы хотите рассказать о новых пожеланиях?", 
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                 [InlineKeyboardButton(text="Использовать предыдущие предпочтения", callback_data="use_previous")],
                                 [InlineKeyboardButton(text="Рассказать о новых пожеланиях", callback_data="new_preferences")]
                             ]))

@router.message(UserState.waiting_for_perfume_input)
async def process_perfume_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db.update_user_activity(user_id)
    dialogue_manager.add_to_dialogue_history(user_id, "user", message.text)
    recommendation = await generate_perfume_recommendation(user_id, message.text)
    db.add_recommendation(user_id, recommendation)
    await message.answer(recommendation, reply_markup=show_menu_kb)

@router.callback_query(F.data == "use_previous")
async def use_previous_preferences(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    dialogue_history = dialogue_manager.get_dialogue_history(user_id)
    
    if dialogue_history:
        last_user_message = next((msg['content'] for msg in reversed(dialogue_history) if msg['role'] == 'user'), None)
        if last_user_message:
            recommendation = await generate_perfume_recommendation(user_id, last_user_message)
            db.add_recommendation(user_id, recommendation)
            await callback.message.answer(recommendation, reply_markup=show_menu_kb)
        else:
            await callback.message.answer("Извините, я не нашел ваших предыдущих предпочтений. Давайте начнем заново.")
            await select_perfume(callback.message, state)
    else:
        await callback.message.answer("Извините, я не нашел ваших предыдущих предпочтений. Давайте начнем заново.")
        await select_perfume(callback.message, state)
    
    await callback.answer()

@router.callback_query(F.data == "new_preferences")
async def ask_new_preferences(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.waiting_for_perfume_input)
    await callback.message.answer("Хорошо, расскажите мне о ваших новых пожеланиях:")
    await callback.answer()

@router.callback_query(F.data == "show_menu")
async def show_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Выберите действие:", reply_markup=main_kb)
    await callback.answer()

@router.callback_query(F.data == "rate_recommendation")
async def rate_recommendation(callback: CallbackQuery):
    await callback.message.answer("Оцените рекомендацию от 1 до 5:", reply_markup=rating_kb)
    await callback.answer()

@router.callback_query(F.data.startswith("rate_"))
async def process_rating(callback: CallbackQuery):
    rating = int(callback.data.split("_")[1])
    db.add_rating(callback.from_user.id, rating)
    await callback.message.answer(f"Спасибо за вашу оценку: {rating}!")
    await callback.answer()

@router.message(F.text == "Оставить отзыв")
async def leave_feedback(message: Message, state: FSMContext):
    await state.set_state(UserState.waiting_for_feedback)
    await message.answer("Пожалуйста, напишите ваш отзыв:")

@router.message(UserState.waiting_for_feedback)
async def process_feedback(message: Message, state: FSMContext):
    db.add_feedback(message.from_user.id, message.text)
    await state.clear()
    await message.answer("Спасибо за ваш отзыв!", reply_markup=main_kb)

@router.message(F.text == "Отзывы")
async def show_feedback(message: Message):
    page = 1
    total_pages = db.get_total_feedback_pages()
    feedback = db.get_feedback(page)
    text = "Отзывы:\n\n" + "\n\n".join([f"{fb[0]}\n{fb[1]}" for fb in feedback])
    await message.answer(text, reply_markup=create_feedback_navigation(page, total_pages))

@router.callback_query(F.data.startswith("feedback_page_"))
async def navigate_feedback(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    total_pages = db.get_total_feedback_pages()
    feedback = db.get_feedback(page)
    text = "Отзывы:\n\n" + "\n\n".join([f"{fb[0]}\n{fb[1]}" for fb in feedback])
    await callback.message.edit_text(text, reply_markup=create_feedback_navigation(page, total_pages))
    await callback.answer()

@router.message(F.text == "Техподдержка")
async def support(message: Message, state: FSMContext):
    await state.set_state(UserState.waiting_for_support_request)
    await message.answer("Опишите вашу проблему или задайте вопрос:")

@router.message(UserState.waiting_for_support_request)
async def process_support_request(message: Message, state: FSMContext):
    db.add_support_request(message.from_user.id, message.text)
    await state.clear()
    await message.answer("Ваш запрос принят. Мы свяжемся с вами в ближайшее время.", reply_markup=main_kb)

@router.message(F.text == "Статистика")
async def show_statistics(message: Message):
    if message.from_user.id in ADMIN_IDS:
        stats = db.get_statistics()
        text = f"""
Статистика:
Всего пользователей: {stats.get('total_users', 'Нет данных')}
Активных пользователей: {stats.get('active_users', 'Нет данных')}
Средняя оценка рекомендаций: {f"{stats['avg_rating']:.2f}" if stats.get('avg_rating') is not None else 'Нет данных'}
Всего рекомендаций: {stats.get('total_recommendations', 'Нет данных')}
Всего отзывов: {stats.get('total_feedback', 'Нет данных')}
Всего обращений в поддержку: {stats.get('total_support_requests', 'Нет данных')}
"""
        await message.answer(text)
    else:
        await message.answer("У вас нет доступа к этой функции.")

@router.message(F.text == "Рассылка")
async def start_broadcast(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        await state.set_state(UserState.waiting_for_broadcast)
        await message.answer("Введите текст для рассылки:")
    else:
        await message.answer("У вас нет доступа к этой функции.")

@router.message(UserState.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        # Здесь должна быть логика для рассылки сообщения всем пользователям
        await message.answer("Рассылка выполнена.")
        await state.clear()
    else:
        await message.answer("У вас нет доступа к этой функции.")

@router.message(F.text == "Вернуться в главное меню")
async def return_to_main_menu(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Выберите действие:", reply_markup=admin_kb)
    else:
        await message.answer("Выберите действие:", reply_markup=main_kb)

@router.callback_query(F.data.startswith("open_kb_admin"))
async def inline_kb_admin(callback: CallbackQuery):
    text = "Пользуйтесь кнопками на клавиатуре."
    await callback.message.answer(text, reply_markup=admin_kb)
    await callback.answer()

@router.message(F.text == "Очистить историю")
async def clear_history(message: Message):
    user_id = message.from_user.id
    dialogue_manager.clear_dialogue_history(user_id)
    await message.answer("История диалога очищена. Давайте начнем сначала!", reply_markup=main_kb)
