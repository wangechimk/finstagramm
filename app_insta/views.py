from itertools import chain

from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .forms import SignUpForm, PostForm, CommentForm, ProfileEditForm, UserEditForm
from .models import Profile, Follow, Comment, Like, Post
from .owner import OwnerCreateView


# Create your views here.
def login(request):
    return render(request, 'registration/login.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # username = form.cleaned_data.get('username')
            # raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=raw_password)
            auth_login(request, user)
            return redirect('app_insta:profile')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required(login_url='login/')
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    following_queryset = request.user.following.all()
    following = [follow.reciever.username for follow in following_queryset]
    return render(request, 'profile.html', {'profile': profile, 'following': following})


@login_required
def EditProfile(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=request.user.user)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('app_insta:profile')
        else:
            context = {'user_form': user_form, 'profile_form': profile_form, 'user_image': request.user.user.photo.url}
            return render(request, 'edit_profile.html', context)
    else:
        u_form = UserEditForm(instance=request.user)
        p_form = ProfileEditForm(instance=request.user.user)
        context = {'user_form': u_form, 'profile_form': p_form, 'user_image': request.user.user.photo.url}
        return render(request, 'edit_profile.html', context)


@login_required(login_url='login/')
def ext_profile(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    following_queryset = request.user.following.all()
    following = [follow.reciever.username for follow in following_queryset]
    return render(request, 'profile.html', {'profile': profile, 'following': following})


class PostCreateView(OwnerCreateView):
    model = Post
    template_name = "post/post_create.html"
    form_class = PostForm

    def get_success_url(self):
        return reverse('app_insta:post_list')


@login_required(login_url='login/')
class FollowView(View):
    @staticmethod
    def post(request):
        user_name = request.POST.get('username')
        user = User.objects.get(username=user_name)
        following = [follow.reciever.username for follow in request.user.following.all()]

        if user_name in following:
            u = Follow.objects.get(owner=request.user, reciever=user).delete()
        else:
            u = Follow.objects.get_or_create(owner=request.user, reciever=user)[0]

        # notification = FollowNotification.objects.create(follow=u)

        html = render_to_string(
            template_name="follow.html",
            context={'following': following, 'profile': get_object_or_404(Profile, user)}
        )

        return JsonResponse({'html': html})


@login_required(login_url='login/')
def feed(request):
    following = [follow.reciever for follow in request.user.following.all()]
    posts = Post.objects.filter(owner__in=following).order_by('-created_at')
    print(posts, 'posts')
    return render(request, 'index.html', {'pictures': posts})


@login_required
def SinglePostView(request, pk):
    post = get_object_or_404(Post, id=pk)
    like_rows = request.user.like_post.values('id')
    liked_posts = [row['id'] for row in like_rows]
    save_rows = request.user.save_post.values('id')
    saved_posts = [row['id'] for row in save_rows]
    comment_form = CommentForm()
    html = render_to_string(
        'post/single_post.html',
        {
            'user': request.user,
            'post': post,
            'comment_form': comment_form,
            'liked_posts': liked_posts,
            'saved_posts': saved_posts
        }
    )
    return JsonResponse(data={'html': html})


#  search view
@method_decorator(csrf_exempt, name='dispatch')
@login_required
def SearchView(request):
    if request.GET.get('q'):
        users = User.objects.filter(username__icontains=request.GET.get('q'))
    else:
        users = User.objects.none()
    return render(request, 'search.html', {'profiles': Profile.objects.filter(user__in=users)})


# @login_required(login_url='login/')
# def new_image(request):
#     current_user = request.user.profile
#     if request.method == 'POST':
#         form = uploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             image = form.save(commit=False)
#             image.profile = current_user
#             image.save()
#         return redirect('profile')
#     else:
#         form = uploadForm()
#     return render(request, 'new_image.html', {'form': form})


@method_decorator(csrf_exempt, name='dispatch')
class followView(View):

    def post(self, request):
        user_name = request.POST.get('username')
        user2 = User.objects.get(username=user_name)

        following_queryset = request.user.following.all()
        following = [follow.reciever.username for follow in following_queryset]

        if (user2.username in following):
            u = Follow.objects.get(owner=request.user, reciever=user2).delete()
        else:
            u = Follow.objects.get_or_create(owner=request.user, reciever=user2)[0]
            notification = FollowNotification.objects.create(follow=u)

        html = render_to_string(
            template_name="follow.html",
            context={'following': following, 'profile': user2}
        )
        response_data = {}
        response_data['html'] = html
        return JsonResponse(response_data)

    #  notification view


# class NotificationDisplayView(View):
#
#     def get(self, request, pk):
#
#         user = User.objects.get(id=pk)
#
#         try:
#             LikeNotification.objects.filter(like__post__owner=user).delete()
#             CommentNotification.objects.filter(comment__post__owner=user).delete()
#             FollowNotification.objects.filter(follow__reciever=user).delete()
#
#         except:
#             pass
#
#         likes = Like.objects.filter(post__owner=user)
#         comments = Comment.objects.filter(post__owner=user)
#         follows = Follow.objects.filter(reciever=user)
#
#         notifications = sorted(
#             chain(likes, comments, follows),
#             key=lambda notification: notification.created_at, reverse=True)
#
#         if len(notifications) <= 1:
#             notifications = None
#
#         html = render_to_string(
#             template_name='notification/notification_display.html',
#             context={'notifications': notifications, 'likes': likes, 'comments': comments, 'follows': follows,
#                      'user': user}
#         )
#         response = {}
#         response['html'] = html
#         return JsonResponse(response)


# post views
@login_required
def PostListView(request):
    template_name = "post/post_list.html"

    context = {}

    following_queryset = request.user.following.all()
    following = [follow.reciever for follow in following_queryset]
    posts = Post.objects.filter(owner__in=following).order_by('-created_at')

    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj

    comment_form = CommentForm()
    context['comment_form'] = comment_form

    rows = request.user.like_post.values('id')
    liked_posts = [row['id'] for row in rows]
    context['liked_posts'] = liked_posts

    rows = request.user.save_post.values('id')
    saved_posts = [row['id'] for row in rows]
    context['saved_posts'] = saved_posts

    return render(request, template_name, context)





@login_required
def PostCreateView(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            Post.objects.create(
                owner=request.user, photo=form.cleaned_data.get('photo'), caption=form.cleaned_data.get('caption')
            )
            return redirect('app_insta:profile')
        else:
            return render(request, "post/post_create.html", {'form': PostForm()})
    else:
        return render(request, "post/post_create.html", {'form': PostForm()})

    # form_class = PostForm
    #
    # def get_success_url(self):
    #     return reverse('app_insta:profile')


@login_required
def CommentCreateView(request, pk):
    post = Post.objects.get(id=pk)
    response_data = {}

    if request.POST.get('action') == 'post':
        text = request.POST.get('text')
        comment = Comment.objects.create(
            text=text,
            owner=request.user,
            post=post,
        )

        if comment.owner != post.owner:
            notification = CommentNotification.objects.get_or_create(comment=comment)

        response_data['text'] = text
        response_data['created_at'] = comment.created_at
        response_data['owner'] = comment.owner.username
        response_data['photo'] = comment.owner.user.photo.url
        response_data['comment_id'] = comment.id
        response_data['post_id'] = pk

        return JsonResponse(response_data)

    return redirect('post_list')


class InboxNotificationView(View):

    def get(self, request, pk):
        if pk != 00:
            inbox = Inbox.objects.get(id=pk)
            InboxNotification.objects.filter(inbox=inbox).delete()

        notifications = InboxNotification.objects.filter(inbox__owner=request.user)
        count = notifications.count()
        notifications = [n.inbox.id for n in notifications]

        html = render_to_string(
            template_name="notification/inbox_notification.html",
            context={"count": count}
        )
        response = {}
        response['html'] = html
        response['notifications'] = notifications

        return JsonResponse(response)


@method_decorator(csrf_exempt, name='dispatch')
@login_required
def SinglePostView(request, pk):
    if request.is_ajax():
        post = get_object_or_404(Post, id=pk)
        like_rows = request.user.like_post.values('id')
        liked_posts = [row['id'] for row in like_rows]
        save_rows = request.user.save_post.values('id')
        saved_posts = [row['id'] for row in save_rows]
        comment_form = CommentForm()
        html = render_to_string('single_post.html', {'user': request.user, 'post': post, 'comment_form': comment_form,
                                                     'liked_posts': liked_posts, 'saved_posts': saved_posts})
        return JsonResponse(data={'html': html})


@method_decorator(csrf_exempt, name='dispatch')
class LikeView(LoginRequiredMixin, View):

    def post(self, request, pk):
        print("Add like PK:", pk)
        post = get_object_or_404(Post, id=pk)
        like = Like(owner=request.user, post=post)

        try:
            like.save()
            if like.owner != post.owner:
                notification = LikeNotification.objects.create(like=like)
        except IntegrityError:
            pass

        html = render_to_string('like_count.html', {'post': post})
        return JsonResponse(data={'html': html})


@method_decorator(csrf_exempt, name='dispatch')
class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        print("Delete like PK:", pk)
        post = get_object_or_404(Post, id=pk)

        try:
            like = Like.objects.get(owner=request.user, post=post).delete()
            notification = LikeNotification.objects.get(like=like).delete()
        except (Like.DoesNotExist, LikeNotification.DoesNotExist) as e:
            pass

        html = render_to_string('like_count.html', {'post': post})
        return JsonResponse(data={'html': html})
