import random
import string

import requests
from rest_framework import status
from rest_framework.utils import json
import username_generator

# Exceptions
class SignUpException(Exception):
    pass

class LoginExcpetion(Exception):
    pass

class CreatePostException(Exception):
    pass

class LikeException(Exception):
    pass

class NoInitialData(Exception):
    pass

class SocialBot(object):
    HEADERS = {
        "content-type": "application/json",
        "Authorization": ""
    }

    SIGN_UP_URL = 'http://localhost:8000/sign-up/'
    LOGIN_URL = 'http://localhost:8000/login/'
    GET_OR_CREATE_POST_URL = 'http://localhost:8000/api/posts/'

    PWD_GEN_CHARS = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"

    def __init__(self, json_data=None):
        if json_data:
            self.json = json_data
        else:
            raise NoInitialData("You didn't set json data.")

        self.number_of_users = self.json['number_of_users'] if self.json.get('number_of_users') else 1
        self.max_posts_per_user = self.json['max_posts_per_user'] if self.json.get('max_posts_per_user') else 1
        self.max_likes_per_user = self.json['max_likes_per_user'] if self.json.get('max_likes_per_user') else 1

    @staticmethod
    def pw_gen(size=8, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def posts_liked(posts):
        num_of_posts = len(posts)
        if len([post for post in posts if post['liked'] > 0]) == num_of_posts:
            return True
        else:
            return False

    def get_posts(self, user):
        self.HEADERS['Authorization'] = 'Bearer ' + user['token']
        response = requests.get(url=self.GET_OR_CREATE_POST_URL, headers=self.HEADERS)
        return json.loads(response.content)

    def signup_users(self):
        self.signed_up_users = []
        number_of_users = self.json['number_of_users']
        while number_of_users:
            username = username_generator.get_uname(min_size=4, max_size=12, underscores=True)
            payload = {
                "username": username,
                "password": self.pw_gen(),
                "email": username + '@bot.com'
            }

            response = requests.post(url=self.SIGN_UP_URL,
                                     data=json.dumps(payload), headers=self.HEADERS)
            self.signed_up_users.append(payload)

            number_of_users -= 1

    def login_users(self):
        self.logged_users = []
        for user in self.signed_up_users:
            response = requests.post(url=self.LOGIN_URL, data=json.dumps(user),
                                     headers=self.HEADERS)
            self.logged_users.append(json.loads(response.content))

    def create_posts(self):
        for user in self.logged_users:
            rand_posts = random.randint(1,self.max_posts_per_user)
            user['posts'] = []
            while rand_posts:
                self.HEADERS['Authorization'] = 'Bearer '+ user['token']
                payload = {
                    "title": user['user']['username'] + " post number " + str(rand_posts),
                    "text": "I am a bot!"
                }

                response = requests.post(url=self.GET_OR_CREATE_POST_URL,
                                         data=json.dumps(payload),
                                         headers=self.HEADERS
                                         )

                if not response.status_code == status.HTTP_201_CREATED:
                    raise CreatePostException(response.content)

                user['posts'].append(json.loads(response.content))

                rand_posts -= 1

    def like_posts(self, post_id, user):
        self.HEADERS['Authorization'] = 'Bearer '+ user['token']
        response = \
            requests.get(url='http://localhost:8000/api/posts/{}/like/'.format(post_id),
                         headers=self.HEADERS)
        if not response.status_code == status.HTTP_201_CREATED:
            raise LikeException(response.content)

    def like_logic(self):
        posting_users = sorted(self.logged_users, key=lambda user: len(user['posts']))
        current_user = self.number_of_users - 1
        reached_max_likes = 1

        while posting_users:
            next_top_user = posting_users[current_user]
            if not next_top_user.get('posts_liked'):
                next_top_user['posts_liked'] = []

            posts = self.get_posts(next_top_user)
            if self.all_posts_liked(posts):
                print("All posts are liked!)")

            no_mxusr_posts = []
            for post in posts:
                if post['user'] != next_top_user['user']['pk'] and \
                   post['id'] not in next_top_user['posts_liked']:
                    no_mxusr_posts.append(post)

            post = random.choice(no_mxusr_posts)
            self.like_posts(post['id'], next_top_user)
            next_top_user['posts_liked'].append(post['id'])

            if len(next_top_user.get('posts_liked')) == self.max_likes_per_user:
                posting_users.pop(current_user)
                reached_max_likes += 1

            current_user -= 1

            if current_user < 0:
                current_user = self.number_of_users - reached_max_likes

        print("All users reached max number of likes!")
