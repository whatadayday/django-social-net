from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt import views as jwt_views
from .views import *


urlpatterns = {
    # path("say-after/<int:delay>/<str:word>", say_after),
    # #path("test/<int:pk>/", Test.as_view()),
    path("user/<int:id>", user_data),
    # path("async/", async_view),
    # path("sync/", sync_view),
    path('signup', CreateUser.as_view(), name='signup'),
    path('signupbg/', CreateUserBg.as_view(), name='signup_bg'),

    path('post/new', CreatePost.as_view(), name='post_new'),
    path('post/<int:post_id>/like', PostLike.as_view(), name='post_like'),
    path('post/<int:post_id>/unlike', PostUnlike.as_view(), name='post_unlike'),
    path('api/token', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
}

urlpatterns = format_suffix_patterns(urlpatterns)
