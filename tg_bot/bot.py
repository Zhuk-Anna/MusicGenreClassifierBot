import aiohttp
from aiohttp import ClientConnectorError
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.request import HTTPXRequest
import os

import tempfile
from config import MAX_FILE_SIZE, API_URL, TMP_DIR, TELEGRAM_TOKEN
from utils import get_file_extension, load_genres
from logger import get_logger


logger = get_logger()


async def on_startup(application):
    timeout = aiohttp.ClientTimeout(total=15)
    session = aiohttp.ClientSession(timeout=timeout)
    application.bot_data["http_session"] = session

    genres = await load_genres()
    application.bot_data["genres"] = genres

    logger.info("HTTP session created")
    logger.info(f"Loaded genres: {genres}")


async def on_shutdown(application):
    session = application.bot_data.get("http_session")
    if session:
        await session.close()
        logger.info("HTTP session closed")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"user={user.id} command=/start")

    keyboard = [
        [KeyboardButton("Загрузить файл")],
        [KeyboardButton("О системе"),
         KeyboardButton("Сообщить об ошибке")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        "🎵 Добро пожаловать в Music Genre Classifier! 🎵\n\n"
        "Я могу определить жанр вашей музыки по аудиофайлу.\n\n"
        "📎 Просто отправьте мне аудиофайл (MP3, WAV, OGG)\n"
        "📊 Максимальный размер: 20 МБ\n\n"
        "Доступные команды:\n"
        "/start - показать это сообщение\n"
        "/help - помощь\n"
        "/info - информация о системе\n\n"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"user={user.id} command=/help")
    genres = context.application.bot_data["genres"]
    help_text = (
        "🎵 Помощь по использованию бота 🎵\n\n"
        "Как использовать:\n"
        "1. Отправьте аудиофайл в формате MP3, WAV или OGG\n"
        "2. Дождитесь обработки (несколько секунд)\n"
        "3. Получите результат классификации жанра\n"
        "Ограничения:\n"
        "• Максимальный размер файла: 20 МБ\n"
        "• Поддерживаемые жанры: " + ", ".join(genres) + "\n\n"
        "Если возникли проблемы - используйте кнопку 'Сообщить об ошибке'"
    )
    await update.message.reply_text(help_text)


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"user={user.id} command=/info")
    genres = context.application.bot_data["genres"]
    info_text = (
        "🎵 Информация о системе 🎵\n\n"
        "Поддерживаемые жанры:\n" +
        "\n".join([f"• {g}" for g in genres]) +
        "\n\nТехнологии:\n"
        "• Модель: CNN + RNN нейросеть\n"
        "• Точность: >90% на тестовых данных\n"
        "• Время обработки: <15 секунд\n\n"
    )
    await update.message.reply_text(info_text)


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"user={user.id} audio received")

    try:
        # Определяем тип файла
        if update.message.audio:
            file = update.message.audio
        elif update.message.voice:
            file = update.message.voice
        elif update.message.document:
            file = update.message.document
        else:
            await update.message.reply_text("❌ Неподдерживаемый тип файла")
            return

        # Проверка размера до скачивания
        if hasattr(file, "file_size") and file.file_size > MAX_FILE_SIZE:
            await update.message.reply_text("❌ Файл слишком большой (максимум 20 МБ)")
            logger.warning(f"user={user.id} tried to send too big file: {file.file_size} bytes")
            return

        # Скачиваем файл
        downloaded_file = await context.bot.get_file(file.file_id)
        file_extension = get_file_extension(file)

        # TMP_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TMP_DIR) as tmpdir:
            temp_path = os.path.join(tmpdir, f"audio.{file_extension}")

            await downloaded_file.download_to_drive(temp_path)
            logger.info(f"user={user.id} file downloaded {temp_path}")

            # Отправляем на API
            # async with aiohttp.ClientSession() as session:
            session = context.application.bot_data["http_session"]
            with open(temp_path, 'rb') as audio_file:
                form_data = aiohttp.FormData()
                form_data.add_field(
                    'file',
                    audio_file,
                    filename=f"audio.{file_extension}",
                    content_type = "audio/*")

                async with session.post(API_URL, data=form_data) as response:
                    logger.info(f"user={user.id} API status={response.status}")
                    if response.status == 200:
                        result = await response.json()
                        # Обработка результата
                        genre = result["genre"]
                        confidence = result["confidence"]
                        response_text = (
                            f"🎵 Результат классификации 🎵\n\n"
                            f"Жанр: {genre}\n"
                            f"Точность: {confidence:.2%}\n\n"
                        )
                        await update.message.reply_text(response_text)
                    elif response.status == 400:
                        result = await response.json()
                        await update.message.reply_text(result["detail"])
                    else:
                        error_text = await response.text()
                        logger.error(f"user={user.id} API error status={response.status} body={error_text}")
        # tmpdir и файл автоматически удаляются
    except ClientConnectorError as e:
        logger.exception(f"user={user.id} error in handle_audio. {e}")
        await update.message.reply_text("Не удалось установить соединение, сервер временно недоступен. Попробуйте позже.")
    except Exception as e:
        logger.exception(f"user={user.id} error in handle_audio. {e}")
        await update.message.reply_text("Произошла ошибка при обработке файла. Попробуйте другой файл.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    logger.info(f"user={user.id} text='{text}'")

    # Если ждём описание ошибки
    if context.user_data.get("awaiting_error_report"):
        if text.lower() not in ["загрузить файл", "о системе", "сообщить об ошибке"]:
            logger.user_error_report(f"user={user.id} error_report='{text}'")

            await update.message.reply_text(
                "✅ Спасибо! Мы получили ваше сообщение об ошибке."
            )
            context.user_data["awaiting_error_report"] = False
            return
        else:
            context.user_data["awaiting_error_report"] = False

    text = text.lower()
    if text == "загрузить файл":
        await update.message.reply_text("📎 Пожалуйста, отправьте аудиофайл для классификации жанра.")
    elif text == "о системе":
        await info_command(update, context)
    elif text == "сообщить об ошибке":
        context.user_data["awaiting_error_report"] = True
        await update.message.reply_text(
            "📝 Опишите пожалуйста проблему, с которой вы столкнулись, в одном сообщении."
        )

    else:
        await update.message.reply_text(
            "🤖 Я не понимаю эту команду. Отправьте мне аудиофайл для классификации "
            "или используйте кнопки меню."
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Exception while handling update:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Произошла внутренняя ошибка. Попробуйте позже."
        )


async def handle_unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Я не могу обрабатывать этот тип сообщения. "
        "Пожалуйста, отправьте аудиофайл или используйте кнопки меню."
    )


def main():
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=300.0,
        write_timeout=120.0,
        pool_timeout=30.0,
    )

    # Создаем приложение
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .request(request)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )
    
    # Добавляем обработчики

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))

    # Аудио/файлы
    application.add_handler(MessageHandler(filters.AUDIO | filters.VOICE | filters.Document.AUDIO, handle_audio))
    # application.add_handler(MessageHandler(filters.AUDIO | filters.VOICE | filters.Document.ALL, handle_audio))

    # Текст
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Всё остальное
    application.add_handler(MessageHandler(
        ~(filters.TEXT | filters.AUDIO | filters.VOICE | filters.Document.AUDIO),
        handle_unsupported
    ))

    # Ошибки
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("Starting Telegram bot")
    logger.info(f"API_URL={API_URL}")
    application.run_polling() # drop_pending_updates=True чтобы удалить старые неотвеченные сообщения


if __name__ == "__main__":
    main()