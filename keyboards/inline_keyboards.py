# Главное меню

start_kb = [
    ("🛌 Мебель для спальни", "sleep_furniture"),
    ("🍽️ Мебель кухни", "kitchen_furniture"),
    ("🛋️ Диваны и кресла", "soft_furniture"),
    ("🍽️ Обеденные группы", "tables_chairs"),
    ("🧰 Комоды и тумбы", "cabinets_commodes"),
    ("🛏️ Каркасы кроватей", "bed_furniture"),
    ("🧴 Матрасы и топперы", "mattresses"),
    ("🚪 Шкафы-купе", "wardrobes"),
    ("ℹ️ О нас и контакты", "about_company"),
    ("🤝 Оптовикам", "cooperation_company"),
]

# Админ меню
admin_kb = [
    ("🗂️ Создать категорию", "new_category_furniture"),
    ("🪑 Добавить товар", "new_furniture"),
    ("🗑️ Удалить товар", "remove_furniture"),
    ("📋 Категории", "list_categories_furniture"),
    ("🤝 Заявки на сотрудничество", "cooperation_requests"),
    # Меняем callback на админский, чтобы не перехватывать общий back_to_main
    ("◀️ Вернуться", "admin_back_to_main")
]

# Кнопка отмены для сотрудничества
cancel_cooperation = [
    ("⏪ Отменить", 'cancel_cooperation')
]

# Кнопка отмены для категорий
build_cancel_kb = [
    ("❌ Отменить", "cancel_category"),
]

country_kb = [
    "🇷🇺 Россия",
    "🇹🇷 Турция"
]

# Страны производства
contry_of_origin_kb = [
    ("🇷🇺 Россия", "russian_origin"),
    ("🇹🇷 Турция", "turkey_origin"),
    ("⬅️ В меню", "back_to_main")
]

# Подкатегории кухонной мебели
kitchen_subcategory_kb = [
    "📏 Прямая кухня",
    "📐 Угловая кухня"
]

# Подкатегории кухонной мебели для inline клавиатуры
kitchen_subcategory_inline_kb = [
    ("📏 Прямая кухня", "straight_kitchen"),
    ("📐 Угловая кухня", "corner_kitchen"),
    ("⬅️ В меню", "back_to_main")
]


def get_accept_cancel_buttons(request_id: int):
    return [
        ("❌ Отклонить", f"cancel_cooperation_requests_{request_id}"),
        ("✅ Одобрить", f"accepted_cooperation_requests_{request_id}"),
        ("⏪ Отмена", "show_requests_cooperation_2")
    ]


more_added_furniture = [
    ("🔄 Добавить еще", "new_furniture"),
]