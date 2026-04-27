from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Post
from .forms import PostForm, UserRegisterForm
from django.contrib import messages

# Create your views here.

def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            posts = Post.objects.all().order_by('-created_at')
        else:
            posts = Post.objects.filter(is_draft=False).union(
                Post.objects.filter(author=request.user)
            ).order_by('-created_at')
    else:
        posts = Post.objects.filter(is_draft=False).order_by('-created_at')
    return render(request, 'blogapp/home.html', {'posts': posts})

def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created. You are now logged in.')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            action = request.POST.get('action', 'publish')
            post.is_draft = action == 'draft'
            post.save()
            if post.is_draft:
                messages.success(request, 'Draft saved successfully.')
            else:
                messages.success(request, 'Post created successfully.')
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'blogapp/create_post.html', {'form': form})

def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    if post.is_draft and not (request.user.is_authenticated and (request.user == post.author or request.user.is_superuser)):
        return redirect('home')
    return render(request, 'blogapp/post_detail.html', {'post': post})
