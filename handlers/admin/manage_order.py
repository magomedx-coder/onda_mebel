from aiogram import Router, F, types

from database.crud import CrudCategory

router = Router()


@router.callback_query(F.data == 'list_categories_furniture')
async def list_categories_furniture_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()

    crud = CrudCategory()
    all_categories = await crud.get_all_categories()

    lst_categories = [(category.name, str(category.id)) for category in all_categories]

    if not lst_categories:
        await callback_query.message.answer("📭 В каталоге пока нет категорий мебели.")
        return

    lines = ["🗂️ Перечень категорий мебели:\n"]
    for idx, (name, id_) in enumerate(lst_categories, start=1):
        lines.append(f"{idx}. {name} — идентификатор: {id_}")

    text = "\n".join(lines)
    await callback_query.message.answer(text)