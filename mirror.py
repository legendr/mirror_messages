
from telethon import events
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from pymongo import MongoClient
import datetime

# file: .
from environs import Env
# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

API_ID = env.int('API_ID')
API_HASH = env.str('API_HASH')
SESSION_STRING = env.str('SESSION_STRING')
DATABASE_URL = env.url('DATABASE_URL')

MY_CHANNEL=env.int('MY_CHANNEL')
SOURCE_CHANNELS =["faceofwar", "anna_news", "rybar", "sashakots", "epoddubny",
                 "russ_orientalist", "vladlentatarsky", "aleksandr_skif", "neoficialniybezsonov", "SIL0VIKI",
                 "boris_rozhin", "voenacher", "grey_zone", "chvkmedia", "Ugolok_Sitha"]

client_mndb = MongoClient(DATABASE_URL)
db = client_mndb.db_telegram
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Обработчик новых сообщений
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler_new_message(event):
    try:
        channel_id=event.message.to_dict()['fwd_from']['from_id']['channel_id']
        post_id=event.message.to_dict()['fwd_from']['channel_post']
        if db.posts.count_documents({"channel_id": channel_id, "post_id":post_id}) == 0:
            db.posts.insert_one({
                "channel_id": channel_id,
                "post_id": post_id,
                "date": datetime.datetime.now()
            })
            await client.forward_messages(MY_CHANNEL, event.message)
        else:
            print("COPY")


        # отправим сообщение в наш канал
        #await client.send_message(TARGET_CHANNEL, event.message)
        # либо вместо переотправки можно репостнуть:
        #await client.forward_messages(-1001507003446, event.message)
        #print(event.message.to_dict()['fwd_from']['from_id']['channel_id']) 
    except Exception as e:
        print(e)

if __name__ == '__main__':
    client.start()
    client.run_until_disconnected()