# -*- coding: utf-8 -*-

import requests, pickle, vk_api, sys, json, logging, os
reload(sys)
sys.setdefaultencoding('utf8')

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

with open('blacklist', 'rb') as file:
    blacklist = pickle.load(file)
    print('blacklist: {}'.format(blacklist))

if __name__ == '__main__':
    session = requests.Session()

    login, password = '', ''
    vk_session = vk_api.VkApi(login, password)
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        sys.exit(0)

    vk = vk_session.get_api()

    try:
        upload = VkUpload(vk_session)
        longpoll = VkLongPoll(vk_session)

        user = vk.users.get(user_ids=107431201)
        print(user[0]['id'])

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.from_chat:

                user_id = int(event.user_id)
                if (blacklist.__contains__(user_id)):

                    log.info('chat:{} id:{} msg:{}'.format(event.chat_id, event.user_id, event.text))
                    vk.messages.delete(message_ids=event.raw[1])


                # else:
                    # print blacklist.__contains__(event.user_id), event.user_id, blacklist
                    # print type(blacklist[1]), type(user_id)
                    # print  'chat:', event.chat_id, ' id:', event.user_id, ' ', event.text

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
                                    message += '> *id' + str(user['id']) + '(' \
                                               + user['first_name'] + ' ' \
                                               + user['last_name'] + ') ' \
                                               + str(user['id']) + '\n'

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
















    except KeyboardInterrupt:
        sys.exit(0)
