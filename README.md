# socialnetwork

# Usage:
* `python manage.py test` unit test
* `python manage.py runserver` run django server
* `python testbot/botsocnet.py` automated bot, create user, posts and emulate user activity


# Directory Structure:
* `djangoserver/` django settings file and packages
* `socialnetwork/` django social network application 
* `testbot/` automated test bot and settings

# Installing:
`docker build -t socnet .` build docker image


# Run:
`docker run --rm -it --entrypoint=bash socnet` run image with shell entrypoint
`python manage.py runserver &` run django server in a background mode

`docker run -p localhost:8000:8000 socnet` for test externally


# Description:
* while running `python manage.py test`
    there is some warnings. it's okay as we test forbidden requests as well
    .WARNING:django.request:Bad Request: /socialnetwork/post/1/like
    WARNING:django.request:Bad Request: /socialnetwork/post/2/like
    WARNING:django.request:Bad Request: /socialnetwork/post/2/unlike
    .WARNING:django.request:Bad Request: /socialnetwork/signup

* models.User.likes_user_ids
    For storing user ids related to post is used list structure serialized as json field.
    This is does not correspond to the normal database form, but has some benefits comparing to regular many2many table
    * Access to one field works faster than select from a one single table.
    * This potential Post2User table will be grown unlimited eventually. So it can be a definite problem with read and update for a big amount of data
    * In our case (social network) we have unlimited posts, but amount of likes for one post is not so big. Averagely it's up to thousand. JSON field size which is 1GB is quite enough for keeping them
    
* CreateUser, CreateUserBg
    * use Hunter API for verifying user email address
    * use Clearbit API to get clearbit peronal info data
    * the clearbit data d as json 'person_info' field in User model 

   Implemented two ways of creating user entity
    * CreateUser
        * use asynchrnous calls for API requests
        * after completing requests returns response to client
    * CreateUserBg
        * calls Hunter API for verifying user email
        * return 'success' response to client 
        * put request to Clearbit data as django background task
        * Note: `python manage.py process_tasks` needs to be run to process background tasks
        
    * to see benchmark statistic set django.conf.settings.LOG_LEVEL = logging.INFO
    

