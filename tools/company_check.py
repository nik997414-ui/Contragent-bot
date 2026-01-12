import os
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from dadata import Dadata
from .base_tool import BaseTool

class CompanyCheckTool(BaseTool):
    """
    Инструмент для проверки контрагентов через DaData.
    Включает расширенный светофор рисков и генерацию PDF.
    """
    
    @property
    def name(self) -> str:
        return "company_check"

    @property
    def description(self) -> str:
        return "Проверка компании по ИНН (Светофор + PDF)"

    def register_handlers(self):
        @self.router.message(lambda msg: msg.text and msg.text.strip().isdigit() and len(msg.text.strip()) in [10, 12])
        async def check_company_handler(message: types.Message):
            api_key = os.getenv("DADATA_API_KEY")
            secret_key = os.getenv("DADATA_SECRET_KEY")
            
            if not api_key or "ur_dadata" in api_key:
                await message.answer("⚠️ Ошибка настройки: Не указан API ключ DaData.")
                return

            # Проверка лимитов
            from database import try_consume_check, get_or_create_user, is_admin
            
            user_id = message.from_user.id
            username = message.from_user.username
            
            # Админы имеют безлимитный доступ
            if is_admin(username):
                checks_left_msg = " (👑 Безлимит)"
            elif not try_consume_check(user_id):
                await message.answer(
                    "🚫 **Лимит бесплатных проверок исчерпан!**\n\n"
                    "Вы использовали свои 3 бесплатные проверки. "
                    "В будущем здесь можно будет купить подписку, а пока — бот в режиме разработки.",
                    parse_mode="Markdown"
                )
                return
            else:
                # Показываем остаток
                user_info = get_or_create_user(user_id)
                checks_left_msg = f" (Осталось проверок: {user_info['checks_left']})" if not user_info['is_premium'] else ""


            status_msg = await message.answer(f"⏳ Ищу информацию о компании...{checks_left_msg}")
            
            try:
                # Инициализация DaData
                dadata = Dadata(api_key, secret_key) if secret_key else Dadata(api_key)
                
                inn = message.text.strip()
                result = dadata.find_by_id("party", inn)
                    
                if not result:
                    await message.answer("❌ Компания с таким ИНН не найдена.")
                    return

                company = result[0]
                data = company['data']
                
                # Используем новый анализатор рисков
                from risk_analyzer import format_risk_report
                report_text = format_risk_report(data)
                
                await message.answer(report_text, parse_mode="Markdown")
                
                # Генерируем PDF
                await status_msg.edit_text("📄 Генерирую PDF-отчет...")
                
                from pdf_generator import generate_pdf_report
                pdf_path = generate_pdf_report(data, user_id)
                
                # Отправляем PDF
                pdf_file = FSInputFile(pdf_path, filename=f"Отчет_{inn}.pdf")
                await message.answer_document(
                    pdf_file,
                    caption="📎 PDF-отчет для приложения к договору"
                )
                
                # Удаляем статусное сообщение
                await status_msg.delete()
            
            except Exception as e:
                await message.answer(f"❌ Произошла ошибка при запросе: {e}")

        @self.router.message(Command("check"))
        async def cmd_check(message: types.Message):
            await message.answer(
                "🔍 **Проверка контрагента**\n\n"
                "Отправьте ИНН компании (10 или 12 цифр) для получения:\n"
                "• Расширенного светофора рисков\n"
                "• PDF-отчета для документов",
                parse_mode="Markdown"
            )
