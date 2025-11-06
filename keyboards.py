from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Дохід", callback_data="type_income"),
         InlineKeyboardButton(text="💸 Витрата", callback_data="type_expense")]
    ])

def get_category_keyboard():
    categories = [
        "🚗 Транспорт", "🍔 Їжа", "📞 Рахунки / зв’язок", "🎁 Подарунки",
        "🎮 Розваги", "👕 Одяг", "💅 Краса та послуги", "☕ Кафе",
        "💊 Аптека та здоров’я", "🏠 Комунальні", "💳 Кредити"
    ]
    buttons = [[InlineKeyboardButton(text=c, callback_data=f"cat_{c}")] for c in categories]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_chart_period_keyboard():
    buttons = [
        [InlineKeyboardButton(text="7 днів", callback_data="chart_7"),
         InlineKeyboardButton(text="30 днів", callback_data="chart_30")],
        [InlineKeyboardButton(text="90 днів", callback_data="chart_90"),
         InlineKeyboardButton(text="Весь час", callback_data="chart_9999")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
