from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards import main_kb, admin_kb, show_menu_kb, rating_kb, create_feedback_navigation
from openai_integration import generate_perfume_recommendation
from config import ADMIN_IDS

router = Router()

class UserState(StatesGroup):
    waiting_for_perfume_input = State()
    waiting_for_feedback = State()
    waiting_for_support_request = State()
    waiting_for_broadcast = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    db.add_user(message.from_user.id, message.from_user.username)
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Добро пожаловать в админ-панель!", reply_markup=admin_kb)
    else:
        await message.answer("Добро пожаловать в AI-консультант по подбору парфюмерии!", reply_markup=main_kb)

@router.message(F.text == "Подобрать парфюм")
async def select_perfume(message: Message, state: FSMContext):
    await state.set_state(UserState.waiting_for_perfume_input)
    await message.answer("Опишите, пожалуйста, какой аромат вы ищете или какие у вас предпочтения:")

@router.message(UserState.waiting_for_perfume_input)
async def process_perfume_input(message: Message, state: FSMContext):
    db.update_user_activity(message.from_user.id)
    recommendation = await generate_perfume_recommendation(message.text)
    db.add_recommendation(message.from_user.id, recommendation)
    await message.answer(recommendation, reply_markup=show_menu_kb)

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
Всего пользователей: {stats['total_users']}
Активных пользователей: {stats['active_users']}
Средняя оценка рекомендаций: {stats['avg_rating']:.2f if stats['avg_rating'] is not None else 'Нет данных'}
Всего рекомендаций: {stats['total_recommendations']}
Всего отзывов: {stats['total_feedback']}
Всего обращений в поддержку: {stats['total_support_requests']}
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
        await message.answer("Выберите действие:", reply_markup=main_kb)
    else:
        await message.answer("Выберите действие:", reply_markup=main_kb)

