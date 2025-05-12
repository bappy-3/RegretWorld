from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import CreateView, UpdateView, ListView, DetailView, View, TemplateView, DeleteView
from App_Feed.models import Blog, Comment, Likes
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from App_Feed.forms import CommentForm
import uuid

# Create your views here.

class MyBlogs(LoginRequiredMixin, TemplateView):
    template_name = 'App_Feed/my_blogs.html'

class CreateBlog(LoginRequiredMixin, CreateView):
    model = Blog
    template_name = 'App_Feed/create_blog.html'
    fields = ('blog_title', 'blog_content', 'blog_image',)

    def form_valid(self, form):
        blog_obj = form.save(commit=False)
        blog_obj.author = self.request.user
        title = blog_obj.blog_title
        blog_obj.slug = title.replace(" ", "-") + "-" + str(uuid.uuid4())
        blog_obj.save()
        return HttpResponseRedirect(reverse('index'))

class BlogList(ListView):
    context_object_name = 'blogs'
    model = Blog
    template_name = 'App_Feed/blog_list.html'

@login_required 
def blog_details(request, slug):
    blog = Blog.objects.get(slug=slug)
    comment_form = CommentForm()
    already_liked = Likes.objects.filter(blog=blog, user= request.user)
    if already_liked:
        liked = True
    else:
        liked = False
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.blog = blog
            comment.save()
            return HttpResponseRedirect(reverse('App_Feed:blog_details', kwargs={'slug':slug}))
    return render(request, 'App_Feed/blog_details.html', context={'blog':blog, 'comment_form':comment_form, 'liked':liked,})

@login_required
def liked(request, pk):
    blog = Blog.objects.get(pk=pk)
    user = request.user
    already_liked = Likes.objects.filter(blog=blog, user=user)
    if not already_liked:
        liked_post = Likes(blog=blog, user=user)
        liked_post.save()
    return HttpResponseRedirect(reverse('App_Feed:blog_details', kwargs={'slug':blog.slug}))

@login_required
def unliked(request, pk):
    blog = Blog.objects.get(pk=pk)
    user = request.user
    already_liked = Likes.objects.filter(blog=blog, user=user)
    already_liked.delete()
    return HttpResponseRedirect(reverse('App_Feed:blog_details', kwargs={'slug':blog.slug}))

# class UpdateBlog(LoginRequiredMixin, UpdateView):
#     model = Blog
#     fields = ('blog_title', 'blog_content', 'blog_image')
#     template_name = 'App_Feed/edit_blog.html'

#     def get_success_url(self, **kwargs):
#         return reverse_lazy('App_Feed:blog_details', kwargs={'slug':self.object.slug})


class UpdateBlog(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ('blog_title', 'blog_content', 'blog_image')
    template_name = 'App_Feed/edit_blog.html'

    def form_valid(self, form):
        blog = form.save(commit=False)

        # If no new image is uploaded, keep the existing one
        if not self.request.FILES.get('blog_image') and self.object.blog_image:
            blog.blog_image = self.object.blog_image

        blog.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self, **kwargs):
        return reverse_lazy('App_Feed:blog_details', kwargs={'slug': self.object.slug})



class DeleteBlog(LoginRequiredMixin, DeleteView):
    model = Blog
    template_name = 'App_Feed/delete_blog.html'
    success_url = reverse_lazy('App_Feed:my_blogs')  # Redirect after deletion

    def get_queryset(self):
        # Ensure users can only delete their own posts
        return Blog.objects.filter(author=self.request.user)


