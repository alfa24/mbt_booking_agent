"""Точка входа: инициализация бота и запуск polling."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from bot.config import get_settings
from bot.handlers.message import router
from bot.services.backend_client import BackendClient
from bot.services.llm import LLMService


def main() -> None:
    """Настраивает логирование, сервисы и запускает polling."""
    settings = get_settings()

    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Configure proxy if set
    session = None
    if settings.proxy_url:
        session = AiohttpSession(proxy=settings.proxy_url)
        logger.info("Using proxy: %s", settings.proxy_url)

    bot = Bot(token=settings.telegram_bot_token, session=session)
    dp = Dispatcher()

    dp["settings"] = settings
    dp["backend"] = BackendClient(settings)
    dp["llm_service"] = LLMService(settings)

    dp.include_router(router)

    logger.info("Бот запущен")
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
