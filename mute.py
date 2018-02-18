# -*- coding: utf-8 -*-

import requests, pickle, vk_api, sys, json, logging, os
reload(sys)
sys.setdefaultencoding('utf8')

from ConfigParser import SafeConfigParser
from requests.exceptions import ReadTimeout
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType

# blacklist = [107431201]
# with open('blacklist', 'wb') as file:
    # pickle.dump(blacklist, file)


log = logging.getLogger(__name__)
log.setLevel('DEBUG')
log_file_url = 'log.log'
file_handler = logging.FileHandler(log_file_url)
formatter = logging.Formatter('%(asctime)s %(message)s', '%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)

f = 'blacklist'
try:
    with open(f, 'rb') as file:
        blacklist = pickle.load(file)
        print('blacklist: {}'.format(blacklist))

except IOError:
    blacklist = []
    print('blacklist: {}'.format(blacklist))

    file = open(f, 'w')
    pickle.dump(blacklist, file)


if __name__ == '__main__':
    session = requests.Session()

    config = SafeConfigParser()
    config.read('config.ini')
    vk_session = vk_api.VkApi(config.get('auth', 'login'), config.get('auth', 'password'))

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        sys.exit(0)

    vk = vk_session.get_api()

    while True:
        try:
            upload = VkUpload(vk_session)
            longpoll = VkLongPoll(vk_session)

            user = vk.users.get(user_ids=107431201)

            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.from_chat:

                    user_id = int(event.user_id)
                    if (blacklist.__contains__(user_id)):

                        log.info('chat:{} id:{} msg:{}'.format(event.chat_id, event.user_id, event.text))
                        vk.messages.delete(message_ids=event.raw[1])

                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.raw[3] == 107431201:
                    command = str(event.text).split()
                    if command[0] == 'mute':

                        if len(command) == 2:
                            if command[1] == 'list':
                                user_ids = ''
                                for b in blacklist:
                                    user_ids += str(b) + ', '

                                users = vk.users.get(user_ids=user_ids)

                                message = ''
                                for user in users:
                                    message += '> *id{}({} {}) {}\n'.format(user['id'],
                                     user['first_name'], user['last_name'], user['id'])
                                if message == '':
                                    message = '> empty'

                                vk.messages.send(user_id=107431201, message=message)

                        elif len(command) == 3:
                            command_id = command[2]

                            if command[1] == 'add':
                                user = vk.users.get(user_ids=command_id)[0]
                                user_id    = user['id']
                                first_name = user['first_name']
                                last_name  = user['last_name']

                                if user_id not in blacklist:
                                    blacklist.append(user_id)
                                    with open('blacklist', 'wb') as file:
                                        pickle.dump(blacklist, file)

                                    msg = '> added *id{}({} {}) {}'.format(user_id, first_name, last_name, user_id)
                                    vk.messages.send(user_id=107431201, message=msg)
                                    print('added {} {} {}'.format(first_name, last_name, user_id))

                                else:
                                    print('{} {} {} is already blacklisted'.format(first_name, last_name, user_id))
                                    vk.messages.send(user_id=107431201, message='> *id{}({} {}) is already blacklisted'.format(user_id, first_name, last_name))

                            if command[1] == 'remove':
                                user = vk.users.get(user_ids=command_id)[0]
                                user_id    = user['id']
                                first_name = user['first_name']
                                last_name  = user['last_name']

                                if user_id in blacklist:
                                    blacklist.remove(user_id)
                                    with open('blacklist', 'wb') as file:
                                        pickle.dump(blacklist, file)

                                    msg = '> removed *id{}({} {})'.format(user_id, first_name, last_name)
                                    vk.messages.send(user_id=107431201, message=msg)
                                    print('removed {} {} {}'.format(first_name, last_name, user_id))

                                else:
                                    print('{} {} {} is not in blacklist'.format(first_name, last_name, user_id))
                                    vk.messages.send(user_id=107431201, message='> *id{}({} {}) is not in blacklist'.format(user_id, first_name, last_name))

        except ReadTimeout as e:
            print('ReadTimeout')

        except ValueError as e:
            print('ValueError')
            print(e)

        except KeyboardInterrupt:
            sys.exit(0)
