
from telethon import events
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from pymongo import MongoClient
import redis
from environs import Env

env = Env()
env.read_env()

API_ID = env.int('API_ID')
API_HASH = env.str('API_HASH')
SESSION_STRING = env.str('SESSION_STRING')
DATABASE_URL = env.str('DATABASE_URL')
SOURCE_CHANNELS = env.list('SOURCE_CHANNELS')
MY_CHANNEL=env.int('MY_CHANNEL')

r = redis.Redis(host='redis', port=6379)
client_mndb = MongoClient(DATABASE_URL)
db = client_mndb.db_telegram
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Обработчик новых сообщений
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler_new_message(event):
    try:
        if event.message.to_dict()['fwd_from'] == None:
            channel_id=event.message.to_dict()['peer_id']['channel_id']
            post_id=event.message.to_dict()['id']
        else:
            channel_id=event.message.to_dict()['fwd_from']['from_id']['channel_id']
            post_id=event.message.to_dict()['fwd_from']['channel_post']
        if r.exists('channel') == 0:
            r.hsetnx('channel', channel_id, post_id)
            r.expire('channel',600)
            await client.forward_messages(MY_CHANNEL, event.message)
        else:
            if r.hsetnx('channel', channel_id, post_id) == 1:
                await client.forward_messages(MY_CHANNEL, event.message)
            else:
                print("COPY")
        # отправим сообщение в наш канал
        #await client.send_message(TARGET_CHANNEL, event.message)
 
    except Exception as e:
        print(e)

if __name__ == '__main__':
    client.start()
    client.run_until_disconnected()   