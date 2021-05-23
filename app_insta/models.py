from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import datetime 
from django.core.validators import RegexValidator
import PIL.Image as Image

# Create your models here.
class Image(models.Model):
    ''' a model for Image posts '''
    image = models.ImageField(upload_to='images/')
    caption = models.TextField()
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True)
    created_on = models.DateTimeField(default=datetime.date.today(), null=True, blank=True)

    class Meta:
        ordering = ['?'] #order randomly on feed

    def save_image(self):
        ''' method to save an image post instance '''
        self.save()

    def delete_image(self):
        '''method to delete an image post instance '''
        self.delete()

    def update_caption(self, new_caption):
        ''' method to update an image's caption '''
        self.caption = new_caption
        self.save()

    @classmethod    
    def get_user_images(cls, user_id):
        ''' method to retrieve all images'''
        img = Image.objects.filter(profile=user_id).all()
        sort = sorted(img, key=lambda t: t.created_on)
        return sort

class Profile(models.Model):
    ''' extended User model'''
    user = models.OneToOneField(User,related_name='user',on_delete=models.CASCADE,default=1)
    photo = models.ImageField(default='default.jpg', upload_to='profile_pics')
    website = models.URLField(default='', blank=True)
    bio = models.TextField(max_length=500, blank=True, default='')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+9999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.photo.path)
        width, height = img.size  # Get dimensions

        if width > 300 and height > 300:
            # keep ratio but shrink down
            img.thumbnail((width, height))

        # check which one is smaller
        if height < width:
            # make square by cutting off equal amounts left and right
            left = (width - height) / 2
            right = (width + height) / 2
            top = 0
            bottom = height
            img = img.crop((left, top, right, bottom))

        elif width < height:
            # make square by cutting off bottom
            left = 0
            right = width
            top = 0
            bottom = width
            img = img.crop((left, top, right, bottom))

        if width > 300 and height > 300:
            img.thumbnail((300, 300))

        img.save(self.photo.path)

    def __str__(self):
        return f'{self.user.username}'
    
    def save_profile(self):
        ''' method to save a user's profile '''
        self.save()

    def delete_profile(self):
        '''method to delete a user's profile '''
        self.delete()

    def update_bio(self, new_bio):
        ''' method to update a users profile bio '''
        self.bio = new_bio
        self.save()

    def update_image(self, user_id, new_image):
        ''' method to update a users profile image '''
        user = User.objects.get(id=user_id)
        self.photo = new_image
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

        Follow.objects.create(owner=instance, reciever=instance)
        rashim_narayan = User.objects.get(username='wangechi_kimani')
        Follow.objects.create(owner=instance, reciever=rashim_narayan)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



class Comment(models.Model):
    ''' a model for comments'''
    related_post = models.ForeignKey('Image', on_delete=models.CASCADE ,default=None)
    name = models.ForeignKey('Profile', on_delete=models.CASCADE)
    comment_body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']
    
    def save_comments(self):
        ''' method to save comment instance '''
        self.save()

    def delete_comment(self):
        '''method to delete comment instance '''
        self.delete()

    def edit_comment(self, new_comment):
        ''' method to edit a comment '''
        self.comment_body = new_comment
        self.save()


    def __str__(self):
        return 'Comment by {self.name}'



class Relation(models.Model):
    ''' model for user relations: follower-following system'''
    follower = models.ForeignKey('Profile', related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey('Profile', related_name='followers', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return '{self.follower} follows {self.followed}' 