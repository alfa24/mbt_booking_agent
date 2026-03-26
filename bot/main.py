"""Точка входа: инициализация бота и запуск polling."""

import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import get_settings
from bot.handlers.message import router
from bot.services.booking import BookingService
from bot.services.llm import LLMService


def main() -> None:
    """Настраивает логирование, сервисы и запускает polling."""
    settings = get_settings()

    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()

    dp["settings"] = settings
    dp["booking_service"] = BookingService()
    dp["llm_service"] = LLMService(settings)

    dp.include_router(router)

    logger.info("Бот запущен")
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
