from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from django.conf import settings
import logging
import time
import asyncio
import httpx

from background_task import background

from .models import Post, User
from .serializers import UserSerializer, PostSerializer

HUNTER_URL = 'https://api.hunter.io/v2/email-verifier?email={email}&api_key=' + settings.HUNTER_API_KEY
CLEARBIT_URL = 'https://person.clearbit.com/v1/people/email/{email}'

logging.basicConfig(level=settings.LOG_LEVEL)


def benchmark(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = func(*args, **kwargs)
        end = time.time()
        logging.info(f'processed for {end - start} secs')
        return return_value

    return wrapper


async def user_verify_and_collect(email: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            hunter_response, clearbit_response = await asyncio.gather(
                client.get(HUNTER_URL.format(email=email)),
                client.get(
                    CLEARBIT_URL.format(email=email),
                    headers={'Authorization': 'Bearer ' + settings.CLEARBIT_API_KEY}
                )
            )

            logging.info(f'Hunter response {hunter_response}')
            logging.info(f'Clearbit response {clearbit_response}')

            response = {}
            if hunter_response.status_code == httpx.codes.OK:
                response['success'] = True
            else:
                response['success'] = False
                response['error'] = 'email is not validated by Hunter API'

            if clearbit_response.status_code == httpx.codes.OK:
                response['clearbit_data'] = clearbit_response.json()

            return response
    except httpx.RequestError as exc:
        return {
            'success': False,
            'error': 'can not valid email'
        }
    except Exception as ext:
        logging.exception(ext)
        return {
            'success': False,
            'error': 'system error'
        }


class CreateUser(APIView):
    '''Create user
    verify email via hunter and get data from clearbit in async mode
    '''

    permission_classes = (AllowAny,)

    @benchmark
    def post(self, request) -> Response:

        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(user_verify_and_collect(user['email']))
        loop.close()

        if not response['success']:
            return Response({
                'error': response['error']
            }, status=status.HTTP_400_BAD_REQUEST)

        if response.get('clearbit_data'):
            serializer.save(person_info=response['clearbit_data'])
        else:
            serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)



@background(schedule=0)
def clearbit_data(email):
    '''Get data from clearbit.com and update user 'person_info' field if success
    :param email:
    :return:
    '''

    clearbit_response = httpx.get(CLEARBIT_URL.format(
        email=user['email']),
        headers={'Authorization': 'Bearer ' + settings.CLEARBIT_API_KEY}
    )

    if clearbit_response.status_code == 200:
        user = User.objects.get(email=email)
        user.person_info = clearbit_response.json()
        user.save()
        log.info('updated person info for user email =', email)


class CreateUserBg(APIView):
    '''Create user
    verify email via hunter
    sent request to clearbit as background task
    'manage.py process_tasks' needs to be started to proceed
    '''

    permission_classes = (AllowAny,)

    @benchmark
    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)

        # Hunter verifier
        try:
            hunter_response = httpx.get(HUNTER_URL.format(email=user['email']))
            if hunter_response.status_code != 200:
                return Response({
                    'error': 'email is not validated by Hunter API'
                }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.HTTPError as e:
            return Response({
                'error': 'non valid email'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        # Clearbit enrichment
        clearbit_data(user['email'])

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CreatePost(APIView):
    '''Create post, set authorized user as creator
    '''

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        post_data = request.data
        serializer = PostSerializer(data=post_data)
        serializer.is_valid(raise_exception=True)
        serializer.save(creator=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostLike(APIView):
    '''Like post
    user cannot like his own post
    '''
    permission_classes = (IsAuthenticated,)

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user_id = request.user.id

        if post.creator_id == user_id:
            return Response(
                {'error': 'user can not like his own post'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user_id in post.like_user_ids:
            return Response(
                 {'error': 'the post is already liked by user'},
                 status=status.HTTP_400_BAD_REQUEST,
             )

        post.like_user_ids.append(user_id)
        post.save()

        response = {
           'post_id': post.id,
           'likes': 1,
        }

        return Response(response, status=status.HTTP_200_OK)


class PostUnlike(APIView):
    '''Unike post
    user cannot unlike his own post
    '''
    permission_classes = (IsAuthenticated,)

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user_id = request.user.id

        if not post.like_user_ids or user_id not in post.like_user_ids:
            return Response(
                {'error': 'the post is not liked by user'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        post.like_user_ids.remove(user_id)
        post.save()

        response = {
            'post_id': post.id,
            'likes': 0,
        }

        return Response(response, status=status.HTTP_200_OK)


