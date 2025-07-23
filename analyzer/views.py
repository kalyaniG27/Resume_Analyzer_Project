from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django import forms
from django.views.decorators.csrf import csrf_exempt
from .utils.gemini import generate_interview_questions
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib import messages
from .forms import RegisterForm, ProfileForm, ResumeForm
from .models import Resume, Profile
import json
from analyzer.utils.gemini import generate_interview_questions
from django.contrib.auth.models import User  # ✅ make sure you import this

def landing_page(request):
    return render(request, 'landingpage.html')

# 🔑 Login
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        linkedin = request.POST.get('linkedin', '').strip()
        github = request.POST.get('github', '').strip()
        
        # Your signup form sets the username to be the email, so we can authenticate directly.
        # This is more robust and avoids the MultipleObjectsReturned error.
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    return render(request, 'login.html')
  

# 🚪 Logout
def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save() # The form's save method now handles User and Profile creation

            # Log the user in automatically after registration and redirect to the dashboard
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created successfully.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form})

# 🏠 Dashboard
@login_required
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user)
    username = request.user.username  # Get the logged in user's username
    return render(request, 'dashboard.html', {
        'resumes': resumes,
        'username': username
    })

# 📁 Upload Resume
@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.ats_score = 75.0  # You can replace with real logic
            resume.domain = "Web Development"  # Replace with logic
            resume.save()
            return redirect('dashboard')
    else:
        form = ResumeForm()
    return render(request, 'upload_resume.html', {'form': form})

# 👤 Profile
@login_required
def profile(request):
    profile = request.user.profile  # Profile model
    return render(request, 'profile.html', {'profile': profile})

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        # Pass request.FILES to handle potential file uploads (like a profile picture) in the future
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        # For a GET request, populate the form with the user's current profile data
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

# 💼 Job Matcher
@login_required
def job_matcher(request):
    return render(request, 'jobmatcher.html')

# 🤖 Interview Prep (Placeholder)
@login_required
def interview_prep(request):
   ''' questions = [
        #"Tell me about a challenging project you've worked on.",
       # "What is your experience with Django and Python?",
       # "How do you handle version control using Git?",
       # "Explain the MVC pattern in Django.",
       # "How do you optimize database queries?"
    ]
    selected_domain = None

    if request.method == 'POST':
        domain = request.POST.get('domain')
        if selected_domain:
            questions = generate_interview_questions(domain)

    return render(request, 'interview_prep.html', {
        'questions': questions,
        
    })'''
   return render(request, 'interview_prep.html')

def generate_questions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            domain = data.get("domain", "")
            count = int(data.get("count", 10))
          #  questions = generate_interview_questions(domain, count)
            # ✅ Dummy questions – replace with Gemini later
            questions = generate_interview_questions(domain, count)
                
        
            return JsonResponse({'questions': questions})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
        


# 📄 Download Interview Questions as PDF (Placeholder)
@login_required
def download_questions_pdf(request):
    return HttpResponse("PDF download feature coming soon.")
