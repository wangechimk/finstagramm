from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'app_insta'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.EditProfile, name='edit_profile'),
    path('profile/<str:username>', views.ext_profile, name='ext_profile'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('follow/', views.followView, name='follow'),
    path('search/', views.SearchView, name='search'),
    path('post-create/', views.PostCreateView, name='post_create'),
    path('post-list', views.PostListView, name='post_list'),
    # path('notification/display/', views.NotificationDisplayView.as_view(), name='notification_display'),
    # path('notification/', views.NotificationView.as_view(), name='notification'),
    # path('notification/display/', views.NotificationDisplayView.as_view(), name='notification_display'),
    # path('<str:username>/', views.profile, name='profile'),
    path('like/', views.Like, name='post_like'),
    path('comment/', views.CommentCreateView, name='post_comment_create'),
    path('like/', views.LikeView, name='post_like'),
    path('unlike/', views.UnlikeView, name='post_unlike'),

]
