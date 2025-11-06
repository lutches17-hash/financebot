from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import get_type_keyboard, get_category_keyboard, get_chart_period_keyboard
from utils import generate_chart

router = Router()


# --- СТАНИ ДЛЯ FSM ---
class AddTransaction(StatesGroup):
    choosing_type = State()
    choosing_category = State()
    entering_amount = State()


def register_handlers(dp, db):

    @dp.message(Command('start'))
    async def start_cmd(message: types.Message):
        await message.answer("👋 Вітаю! Я FinanceBot.\nВикористовуйте команди /add, /summary, /list, /chart")

    # --- додати транзакцію ---
    @dp.message(Command('add'))
    async def add_cmd(message: types.Message, state: FSMContext):
        await state.set_state(AddTransaction.choosing_type)
        await message.answer("Оберіть тип операції:", reply_markup=get_type_keyboard())

    # --- вибір типу ---
    @dp.callback_query(lambda c: c.data.startswith("type_"))
    async def type_selected(callback: types.CallbackQuery, state: FSMContext):
        user_type = callback.data.split("_")[1]
        await state.update_data(type=user_type)
        await state.set_state(AddTransaction.choosing_category)
        await callback.message.edit_text(
            f"Тип: {user_type}\nОберіть категорію:",
            reply_markup=get_category_keyboard()
        )

    # --- вибір категорії ---
    @dp.callback_query(lambda c: c.data.startswith("cat_"))
    async def cat_selected(callback: types.CallbackQuery, state: FSMContext):
        category = callback.data.split("_", 1)[1]
        await state.update_data(category=category)
        await state.set_state(AddTransaction.entering_amount)
        await callback.message.edit_text(f"Введіть суму для категорії: {category}")
        await callback.answer()

    # --- введення суми ---
    @dp.message(lambda m: m.text.replace('.', '', 1).isdigit())
    async def add_amount(message: types.Message, state: FSMContext):
        data = await state.get_data()
        user_type = data.get("type")
        category = data.get("category")
        amount = float(message.text)

        await db.add_transaction(message.from_user.id, user_type, category, amount, None)
        await message.answer(f"✅ Додано {user_type} {amount} грн у категорію {category}.")
        await state.clear()

    # --- підсумок ---
    @dp.message(Command('summary'))
    async def summary_cmd(message: types.Message):
        data_all = await db.get_summary(message.from_user.id)
        data_month = await db.get_summary(message.from_user.id, 30)
        
        def fmt(data):
            if not data:
                return "—"
            lines = [f"{k}: {v:.2f} грн" for k, v in data.items()]
            return "\n".join(lines)

        txt = (
            "📊 <b>Зведення витрат</b>\n\n"
            f"💰 <b>Всього:</b>\n{fmt(data_all)}\n\n"
            f"📅 <b>За останні 30 днів:</b>\n{fmt(data_month)}"
    )

        await message.answer(txt, parse_mode="HTML")


    # --- список транзакцій ---
    @dp.message(Command('list'))
    async def list_cmd(message: types.Message):
        rows = await db.list_transactions(message.from_user.id)
        if not rows:
            await message.answer("Немає транзакцій.")
            return
        text = "🧾 Останні транзакції:\n"
        for r in rows:
            text += f"{r['created_at']:%Y-%m-%d}: {r['type']} {r['amount']} грн ({r['category']})\n"
        await message.answer(text)

    # --- графік ---
    @dp.message(Command('chart'))
    async def chart_cmd(message: types.Message):
        await message.answer("Оберіть період:", reply_markup=get_chart_period_keyboard())

    @dp.callback_query(lambda c: c.data.startswith("chart_"))
    async def chart_period(callback: types.CallbackQuery):
        days = int(callback.data.split("_")[1])

        data = await db.get_by_category(callback.from_user.id, days)
        if not data:
            await callback.message.answer("Немає даних для графіка.")
            return

        # Генеруємо графік
        path = generate_chart(data, days)

        # Формуємо ТОП-3 категорії
        sorted_data = sorted(data, key=lambda x: x[1], reverse=True)
        top3 = sorted_data[:3]
        top_text = "\n".join([f"🏅 {c}: {a:.2f} грн" for c, a in top3])
        total_sum = sum(a for _, a in data)

        caption = (
            f"📊 Витрати за останні {days} днів\n\n"
            f"💰 <b>Разом:</b> {total_sum:.2f} грн\n\n"
            f"<b>Топ-3 категорії:</b>\n{top_text}"
        )

        await callback.message.answer_photo(
            photo=types.FSInputFile(path),
            caption=caption,
            parse_mode="HTML"
        )
