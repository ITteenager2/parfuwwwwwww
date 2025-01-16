from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Подобрать парфюм")],
        [KeyboardButton(text="Мои рекомендации")],
        [KeyboardButton(text="Оставить отзыв")],
        [KeyboardButton(text="Отзывы")],
        [KeyboardButton(text="Техподдержка")]
    ],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Статистика")],
        [KeyboardButton(text="Рассылка")],
        [KeyboardButton(text="Вернуться в главное меню")]
    ],
    resize_keyboard=True
)

show_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Показать меню", callback_data="show_menu")],
        [InlineKeyboardButton(text="Оценить рекомендацию", callback_data="rate_recommendation")]
    ]
)

rating_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=str(i), callback_data=f"rate_{i}") for i in range(1, 6)]
    ]
)

def create_feedback_navigation(current_page, total_pages):
    keyboard = []
    if current_page > 1:
        keyboard.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"feedback_page_{current_page-1}"))
    if current_page < total_pages:
        keyboard.append(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"feedback_page_{current_page+1}"))
    return InlineKeyboardMarkup(inline_keyboard=[keyboard])

