from django.contrib.auth.forms import UsernameField
from django.shortcuts import render,redirect,HttpResponseRedirect, get_object_or_404
from .models import Image, Profile,Follow, Comment,Like, Relation
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from .forms import uploadForm ,SignUpForm
from django.views import View
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from .models import Profile,Post,Inbox
from .models import LikeNotification, CommentNotification, FollowNotification,InboxNotification
from itertools import chain
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.urls import reverse, reverse_lazy
from .owner import  OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView


# Create your views here.
@login_required(login_url='login/')
def feed(request):
    pictures = Image.objects.all()
    return render(request, 'index.html',{'pictures':pictures})

@login_required(login_url='login/')
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    following_queryset = request.user.following.all()
    following = [follow.reciever.username for follow in following_queryset]
    return render(request, 'profile.html',{'profile':profile,'following':following}) 

def login(request):
    return render (request, 'registration/login.html')  

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user=form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            auth_login(request, user)
            return redirect('app_insta:profile')
    else:
        form = SignUpForm()
    return render(request,'registration/signup.html', {'form':form})
 
#  search view
@method_decorator(csrf_exempt, name='dispatch')
@login_required
def SearchView(request):
    if request.is_ajax():
        url_parameter = request.GET.get("q")
        if url_parameter:
            profiles = User.objects.filter(username__icontains=url_parameter)
        else:
            profiles = None

        html = render_to_string(
            template_name="search.html", 
            context={"profiles": profiles}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict)

@login_required(login_url='login/')
def new_image(request):
    current_user = request.user.profile
    if request.method == 'POST':
        form = uploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.profile = current_user
            image.save()
        return redirect('profile')
    else:
        form = uploadForm()
    return render(request, 'new_image.html', {'form':form}) 

@method_decorator(csrf_exempt, name='dispatch')
class followView(View):

    def post(self, request):
        user_name = request.POST.get('username')
        user2 = User.objects.get(username=user_name)

        following_queryset = request.user.following.all()
        following = [follow.reciever.username for follow in following_queryset]

        if(user2.username in following):
            u = Follow.objects.get(owner=request.user, reciever=user2).delete()
        else:
            u = Follow.objects.get_or_create(owner=request.user, reciever=user2)[0]
            notification = FollowNotification.objects.create(follow=u)

        html = render_to_string(
            template_name="follow.html",
            context={'following':following, 'profile':user2}
        )
        response_data = {}
        response_data['html'] = html
        return JsonResponse(response_data)    


#  notification view      
class NotificationDisplayView(View):

    def get(self, request, pk):
        
        user = User.objects.get(id=pk)

        try:
            LikeNotification.objects.filter(like__post__owner=user).delete()
            CommentNotification.objects.filter(comment__post__owner=user).delete()
            FollowNotification.objects.filter(follow__reciever=user).delete()

        except:
            pass
        
        likes = Like.objects.filter(post__owner=user)
        comments = Comment.objects.filter(post__owner=user)
        follows = Follow.objects.filter(reciever=user)
        
        notifications = sorted(
            chain(likes, comments, follows),
            key=lambda notification: notification.created_at, reverse=True)

        if len(notifications) <= 1:
            notifications = None

        html = render_to_string(
            template_name='notification/notification_display.html', 
            context = {'notifications':notifications, 'likes':likes, 'comments':comments, 'follows':follows, 'user':user}
        )
        response = {}
        response['html'] = html
        return JsonResponse(response)

# post views
@login_required
def PostListView(request):
    template_name = "post/post_list.html"

    context = {}

    following_queryset = request.user.following.all()
    following = [follow.reciever for follow in following_queryset]
    posts = Post.objects.filter(owner__in = following).order_by('-created_at')
    
    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj

    comment_form = CommentForm()
    context['comment_form'] = comment_form

    rows = request.user.like_post.values('id')
    liked_posts = [ row['id'] for row in rows ]
    context['liked_posts'] = liked_posts

    rows = request.user.save_post.values('id')
    saved_posts = [ row['id'] for row in rows ]
    context['saved_posts'] = saved_posts

    return render(request, template_name, context)



class PostCreateView(OwnerCreateView):
    model = Post
    template_name = "post/post_create.html"
    form_class = PostForm

    def get_success_url(self):
        return reverse('post_list')



@login_required
def CommentCreateView(request, pk):
    post = Post.objects.get(id=pk)
    response_data = {}
    
    if request.POST.get('action') == 'post':
        text = request.POST.get('text')
        comment = Comment.objects.create(
            text = text,
            owner = request.user,
            post = post,
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
        notifications = [ n.inbox.id for n in notifications ]
        

        html = render_to_string(
            template_name="notification/inbox_notification.html", 
            context={"count": count}
        )
        response = {}
        response['html'] = html
        response['notifications'] = notifications

        return JsonResponse(response)
        
        