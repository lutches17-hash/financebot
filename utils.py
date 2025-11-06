import os
import matplotlib.pyplot as plt

def generate_chart(data, days):
    """
    Генерує кругову діаграму витрат по категоріях.
    data — список кортежів [(category, amount), ...]
    days — кількість днів (для підпису графіка)
    """

    # створюємо папку charts, якщо її ще немає
    os.makedirs("charts", exist_ok=True)
    path = f"charts/chart_{days}.png"

    if not data:
        return None

    # розділяємо категорії та суми
    categories = [c for c, _ in data]
    amounts = [a for _, a in data]

    # автогенерація кольорів
    colors = plt.cm.tab20.colors[:len(categories)]

    # створюємо фігуру
    plt.figure(figsize=(7, 7), facecolor="#f9f9f9")

    # функція форматування тексту на секторах
    def fmt(pct, allvals):
        absolute = int(round(pct / 100. * sum(allvals)))
        return f"{pct:.1f}%\n({absolute} грн)"

    # будуємо кругову діаграму
    wedges, texts, autotexts = plt.pie(
        amounts,
        labels=categories,
        colors=colors,
        autopct=lambda pct: fmt(pct, amounts),
        startangle=120,
        textprops=dict(color="black", fontsize=9),
        wedgeprops={"linewidth": 1, "edgecolor": "white"}
    )

    # заголовок
    plt.title(
        f"📊 Витрати за останні {days} днів",
        fontsize=14,
        weight="bold",
        pad=20
    )

    # додаємо легенду збоку
    plt.legend(
        wedges,
        categories,
        title="Категорії",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=9
    )

    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()

    return path
