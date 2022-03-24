
from datetime import datetime
from telethon import events
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
import redis
from environs import Env

env = Env()
env.read_env()

API_ID = env.int('API_ID')
API_HASH = env.str('API_HASH')
SESSION_STRING = env.str('SESSION_STRING')
SOURCE_CHANNELS = env.list('SOURCE_CHANNELS')
MY_CHANNEL=env.int('MY_CHANNEL')

r = redis.Redis(host='redis', port=6379)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler_new_message(event):
    try:
        if event.message.to_dict()['fwd_from'] == None:
            channel_id=event.message.to_dict()['peer_id']['channel_id']
            post_id=event.message.to_dict()['id']
            print(f"{datetime.now()} ORIGINAL {channel_id}:{post_id}")
        else:
            channel_id=event.message.to_dict()['fwd_from']['from_id']['channel_id']
            post_id=event.message.to_dict()['fwd_from']['channel_post']
            print(f"{datetime.now()} FORWARD {channel_id}:{post_id}")
        if r.exists('channel') == 0:
            r.sadd('channel', f'{channel_id}:{post_id}')
            r.expire('channel', 86400)
            await client.forward_messages(MY_CHANNEL, event.message)
            print(f"{datetime.now()} NOT EXISTS->ADD IN SET->SEND MESSAGE {channel_id}:{post_id}")
        else:
            if r.sismember('channel', f'{channel_id}:{post_id}') == 0:
                r.sadd('channel', f'{channel_id}:{post_id}')
                await client.forward_messages(MY_CHANNEL, event.message)
                print(f"{datetime.now()} ADD TO SET->SEND MESSAGE {channel_id}:{post_id}")
            else:
                print(f"{datetime.now()} COPY {channel_id}:{post_id}")
 
    except Exception as e:
        print(e)

if __name__ == '__main__':
    client.start()
    client.run_until_disconnected()   