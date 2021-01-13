from django.conf import settings

import logging
LOG_LEVEL = logging.INFO

settings.configure(
    SECRET_KEY='@_zv8)b=2vfkf+plh&5-d&f3-&p&$9c@^j#t&7yw1aos(7fx6m',
    ROOT_URLCONF=__name__,
)