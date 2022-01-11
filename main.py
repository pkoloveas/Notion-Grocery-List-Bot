from bot import Bot
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    bot = Bot()
    bot.run()
