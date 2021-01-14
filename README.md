# socialnetwork

docker build -t socnet .
docker run --rm -it --entrypoint=bash socnet

python manage.py test
.WARNING:django.request:Bad Request: /socialnetwork/post/1/like
WARNING:django.request:Bad Request: /socialnetwork/post/2/like
WARNING:django.request:Bad Request: /socialnetwork/post/2/unlike
.WARNING:django.request:Bad Request: /socialnetwork/signup


python manage.py runserver&

python testbot/botsocnet.py

docker run -p localhost:8000:8000 socnet


post_like_ids 
many 2 many

UserLike
UserLikeBg

