from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
# class Image(models.Model):
#     ''' a model for Image posts '''
#     image = models.ImageField(upload_to='img/')
#     caption = models.TextField()
#     profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
#     likes = models.ManyToManyField(User, blank=True)
#     created_on = models.DateTimeField(default=datetime.datetime.now(), null=True, blank=True)
#
#     class Meta:
#         ordering = ['?']  # order randomly on feed
#
#     def save_image(self):
#         """ method to save an image post instance """
#         self.save()
#
#     def delete_image(self):
#         """method to delete an image post instance """
#         self.delete()
#
#     def update_caption(self, new_caption):
#         """ method to update an image's caption """
#         self.caption = new_caption
#         self.save()
#
#     @classmethod
#     def get_user_images(cls, user_id):
#         """ method to retrieve all images"""
#         img = Image.objects.filter(profile=user_id).all()
#         sort = sorted(img, key=lambda t: t.created_on)
#         return sort


class Profile(models.Model):
    """ extended User model"""
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE, default=1)
    photo = models.ImageField(default='default.jpeg', upload_to='img')
    website = models.URLField(default='', blank=True)
    bio = models.TextField(max_length=500, blank=True, default='')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+9999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    # def save(self, *args, **kwargs):
    #     super().save()
    #
    #     img.save(self.photo.path)

    def __str__(self):
        return f'{self.user.username}'

    def save_profile(self):
        """ method to save a user's profile """
        self.save()


class Follow(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    reciever = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('owner', 'reciever')

    def __str__(self):
        return f'{self.owner.username} follows {self.reciever.username}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Post(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_posts')
    photo = models.ImageField(upload_to="posts")
    caption = models.CharField(max_length=250, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    comments = models.ManyToManyField(User, through='Comment', related_name='comment_post')
    likes = models.ManyToManyField(User, through='Like', related_name='like_post')
    saves = models.ManyToManyField(User, through='Save', related_name='save_post')

    def save(self, *args, **kwargs):
        super().save()

    def __str__(self):
        return f'{self.owner.username}: {self.caption[:15]}...'


class Comment(models.Model):
    """ a model for comments """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    text = models.CharField(max_length=250, null=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f'{self.owner.username}\'s comment on "{self.post.caption[:15]}..." post: {self.text}'


class Relation(models.Model):
    """ model for user relations: follower-following system """
    """ model for user relations: follower-following system """
    follower = models.ForeignKey('Profile', related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey('Profile', related_name='followers', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return '{self.follower} follows {self.followed}'


class Like(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('owner', 'post')

    def __str__(self):
        return '%s likes %s... post' % (self.owner.username, self.post.caption[:15])


class Save(models.Model):
    owner = models.ForeignKey(User, related_name='save_owner', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_saves')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('owner', 'post')

    def __str__(self):
        return '%s saved %s... post' % (self.owner.username, self.post.caption[:15])
