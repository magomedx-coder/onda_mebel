from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from database.crud import CrudCooperation
from keyboards.inline_keyboards import cancel_cooperation, start_kb
from keyboards.keyboard_creator import make_row_inline_keyboards
from states.states import CooperationStates

router = Router()


@router.callback_query(F.data == 'cooperation_company')
async def start_cooperation_application(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await callback_query.message.answer(
        "📩 Опишите ваше предложение по сотрудничеству в свободной форме.\n"
        "Мы внимательно рассмотрим обращение и ответим в ближайшее время.",
        reply_markup=make_row_inline_keyboards(cancel_cooperation)
    )

    await state.set_state(CooperationStates.text_requests)


@router.message(CooperationStates.text_requests, F.text)
async def receive_cooperation_text(message: types.Message, state: FSMContext):
    get_text = message.text
    create_requests = await CrudCooperation().create_request(
        message.from_user.id,
        message.from_user.username,
        get_text
    )

    if create_requests:
        await message.answer("✅ Спасибо за обращение!\n"
                             "Ваша заявка отправлена. Мы свяжемся с вами как можно скорее.")
        await state.clear()


@router.callback_query(F.data == 'cancel_cooperation')
async def cancel_cooperation_request(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Заявка на сотрудничество отменена.")
    await callback.answer()