# Как получить токены для бота

## Telegram Bot Token

1. Открой Telegram и найди бота **@BotFather**
2. Отправь команду `/newbot`
3. Придумай имя для бота (отображаемое имя)
4. Придумай username для бота (должен заканчиваться на `bot`, например `my_booking_bot`)
5. BotFather выдаст токен вида `123456789:ABCdefGHIjklMNOpqrSTUvwxyz` — сохрани его в `.env` как `BOT_TOKEN`

Подробнее: https://core.telegram.org/bots/tutorial#obtain-your-bot-token

---

## OpenRouter API Key

1. Перейди на https://openrouter.ai/
2. Нажми **Sign In** и зарегистрируйся (через Google, GitHub или email)
3. После входа открой раздел **Keys**: https://openrouter.ai/keys
4. Нажми **Create Key**, введи название ключа
5. Скопируй созданный ключ — сохрани его в `.env` как `OPENROUTER_API_KEY`

Документация: https://openrouter.ai/docs/quickstart

---

## Настройка .env

После получения токенов создай файл `.env` в корне проекта:

```bash
BOT_TOKEN=your_telegram_bot_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

⚠️ Никогда не коммить `.env` в репозиторий — файл уже добавлен в `.gitignore`.
