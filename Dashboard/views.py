from django.http import FileResponse, HttpResponse, JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import UserFile, Task
from groups.models import Group
import json
import re
import os
from django.core.cache import cache
import logging
import requests
from datetime import datetime

FLASK_API_URL = "https://harmanpreet1976.pythonanywhere.com/"

# Set up logging
logger = logging.getLogger('Dashboard.views')

# Helper function for password validation
def validate_password(password):
    if len(password) < 8:
        return 'Password must be at least 8 characters long'
    if not re.search(r'[A-Z]', password):
        return 'Password must contain at least one uppercase letter'
    if not re.search(r'[a-z]', password):
        return 'Password must contain at least one lowercase letter'
    if not re.search(r'\d', password):
        return 'Password must contain at least one number'
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return 'Password must contain at least one special character'
    return ''

# Helper function for username validation
def validate_username(username):
    if ' ' in username:
        return 'Username cannot contain spaces'
    if len(username) < 3:
        return 'Username must be at least 3 characters long'
    return ''

# Home view (Homepage)
def home_view(request):
    context = {'user': request.user}
    return render(request, 'home.html', context)

# API endpoint to check username availability
@csrf_exempt
def check_username(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')

            if not username:
                logger.error("Missing username in check_username request")
                return JsonResponse({'error': 'Username is required'}, status=400)

            username_error = validate_username(username)
            if username_error:
                logger.error(f"Invalid username: {username_error}")
                return JsonResponse({'error': username_error}, status=400)

            if User.objects.filter(username=username).exists():
                logger.info(f"Username {username} already exists")
                return JsonResponse({'error': 'Username already exists'}, status=400)

            logger.info(f"Username {username} is available")
            return JsonResponse({'success': True})
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in check_username: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in check_username: {str(e)}")
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    logger.error("Invalid request method for check_username")
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# API endpoint to send OTP
@csrf_exempt
def send_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp = data.get('otp')

            if not email or not otp:
                logger.error("Missing email or OTP in request")
                return JsonResponse({'error': 'Email and OTP are required'}, status=400)

            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                logger.error(f"Invalid email format: {email}")
                return JsonResponse({'error': 'Invalid email address'}, status=400)

            # Send email
            subject = 'Your OTP for Planit Email Verification'
            message = f'Your OTP is: {otp}\nThis OTP is valid for 5 minutes.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]

            try:
                logger.info(f"Attempting to send OTP email to {email}")
                send_mail(
                    subject,
                    message,
                    from_email,
                    recipient_list,
                    fail_silently=False,
                )
                logger.info(f"OTP email sent successfully to {email}")
            except Exception as e:
                logger.error(f"Failed to send email to {email}: {str(e)}")
                error_msg = str(e).lower()
                if 'authentication' in error_msg:
                    return JsonResponse({'error': 'SMTP authentication failed. Check email credentials.'}, status=500)
                elif 'connection' in error_msg:
                    return JsonResponse({'error': 'SMTP connection failed. Check network or SMTP settings.'}, status=500)
                return JsonResponse({'error': f'Email sending failed: {str(e)}'}, status=500)

            # Store OTP in cache
            cache.set(f'otp_{email}', otp, timeout=300)
            logger.info(f"OTP {otp} stored in cache for {email}")

            return JsonResponse({'success': True})
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in send_otp: {str(e)}")
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    logger.error("Invalid request method for send_otp")
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# API endpoint for login
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            username_error = validate_username(username)
            if username_error:
                return JsonResponse({'error': username_error}, status=400)

            password_error = validate_password(password)
            if password_error:
                return JsonResponse({'error': password_error}, status=400)

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/'})
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return render(request, 'signup.html')

# API endpoint for registration
@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            username_error = validate_username(username)
            if username_error:
                return JsonResponse({'error': username_error}, status=400)

            password_error = validate_password(password)
            if password_error:
                return JsonResponse({'error': password_error}, status=400)

            if not email or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                return JsonResponse({'error': 'Invalid email address'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)

            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            cache.delete(f'otp_{email}')
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return render(request, 'signup.html')

# Logout view
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'User logged out successfully')
    return redirect('home')

# Dashboard view
@login_required
def dashboard_view(request):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "username": request.user.username
    }
    try:
        response = requests.get(f"{FLASK_API_URL}/tasks", json=data, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        tasks = response.json()
        logger.info(f"Successfully fetched tasks: {tasks}")

        # Get current date
        current_date = datetime.now().strftime('%Y-%m-%d')

        return render(request, 'dashboard.html', {
            'tasks': tasks,
            'current_date': current_date  # Pass current date to template
        })
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch tasks: {str(e)}")
        messages.error(request, "Failed to fetch tasks.")
        return render(request, 'dashboard.html', {
            'tasks': [],
            'current_date': datetime.now().strftime('%Y-%m-%d')  # Default to current date if there's an error
        })

# Add task
def add_task(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            task_desc = request.POST.get('task')
            date = request.POST.get('date')
            priority = request.POST.get('priority') == 'true'
            completed = request.POST.get('completed') == 'true'
            if not all([title, task_desc, date]):
                return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)

            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "title": title,
                "task": task_desc,
                "date": date,
                "priority": priority,
                "completed": completed,
                "username": request.user.username
            }
            response = requests.post("https://harmanpreet1976.pythonanywhere.com/tasks", json=data, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the Flask response
            flask_response = response.json()
            if flask_response.get("msg") == "Task added successfully":
                # Fetch the newly added task to get its ID (optional, if needed)
                tasks_response = requests.get(f"https://harmanpreet1976.pythonanywhere.com/tasks", headers=headers)
                tasks_response.raise_for_status()
                tasks = tasks_response.json()
                new_task = next((task for task in tasks if task["title"] == title and task["username"] == request.user.username), None)
                task_id = new_task["id"] if new_task else None

                return JsonResponse({'success': True, 'task_id': task_id})
            else:
                return JsonResponse({'success': False, 'error': 'Failed to add task on Flask server'}, status=500)

        except requests.exceptions.RequestException as e:
            logger.error(f"Add Task - Flask API Request Error: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Flask API error: {str(e)}'}, status=500)
        except Exception as e:
            logger.error(f"Add Task - Error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def update_task(request):
    if request.method == 'POST':
        try:
            task_id = request.POST.get('task_id')
            title = request.POST.get('title')
            task_desc = request.POST.get('task')
            date = request.POST.get('date')
            priority = request.POST.get('priority') == 'true'
            completed = request.POST.get('completed') == 'true'

            data = {
                "title": title,
                "task": task_desc,
                "date": date,
                "priority": priority,
                "completed": completed,
                "username": request.user.username
            }

            response = requests.put(f"{FLASK_API_URL}/tasks/{task_id}", json=data)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    if request.method == 'POST':
        try:
            task_id = request.POST.get('task_id')
            title = request.POST.get('title')
            task_desc = request.POST.get('task')
            date = request.POST.get('date')
            priority = request.POST.get('priority') == 'true'
            completed = request.POST.get('completed') == 'true'
            if not all([task_id, title, task_desc, date]):
                return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)

            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "title": title,
                "task": task_desc,
                "date": date,
                "priority": priority,
                "completed": completed,
                "username": request.user.username,
            }
            response = requests.put(f"https://harmanpreet1976.pythonanywhere.com/tasks/{task_id}", json=data, headers=headers)
            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
        except Exception as e:
            logger.error(f"Update Task - Error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

# Delete task
@csrf_exempt
def delete_task(request):
    if request.method == 'POST':
        try:
            task_id = request.POST.get('task_id')
            print(task_id)
            headers = {
                "Content-Type": "application/json"
            }
            data={
                "username":request.user.username
            }
            if not task_id:
                return JsonResponse({'success': False, 'error': 'Task ID is required'}, status=400)
            # task = Task.objects.get(id=task_id, username=request.user)
            # task.delete()
            response=requests.delete(f'{FLASK_API_URL}/tasks/{task_id}',json=data,headers=headers)

            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

# Pricing view
def pricing_view(request):
    return render(request, 'pricing.html')

# User details view
@login_required
def user_details_view(request):
    user = request.user
    groups = (user.group_memberships.all() |
              user.created_groups.all() |
              Group.objects.filter(allowed_emails__contains=user.email)).distinct()

    # Fetch tasks from Flask API instead of local model
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "username": user.username
    }
    try:
        response = requests.get(f"{FLASK_API_URL}/tasks", json=data, headers=headers)
        response.raise_for_status()
        tasks = response.json()
        task_count = len(tasks)  # Count tasks returned from Flask
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch tasks for user details: {str(e)}")
        tasks = []
        task_count = 0

    context = {
        'user': user,
        'groups': groups,
        'task_count': task_count,
    }
    return render(request, 'user_details.html', context)

# File manager
@login_required
def file_manager(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')

        if title and file:
            UserFile.objects.create(
                user=request.user,
                title=title,
                file=file
            )
            messages.success(request, 'File uploaded successfully!')
            return redirect('file_manager')
        else:
            messages.error(request, 'Both title and file are required.')

    user_files = UserFile.objects.filter(user=request.user)
    return render(request, 'file_manager.html', {'user_files': user_files})

# Delete file
@login_required
def delete_file(request, file_id):
    file = get_object_or_404(UserFile, id=file_id, user=request.user)
    file.file.delete()
    file.delete()
    messages.success(request, 'File deleted successfully!')
    return redirect('file_manager')

# Serve file
@login_required
def serve_file(request, file_id):
    user_file = get_object_or_404(UserFile, id=file_id, user=request.user)
    file_path = user_file.file.path

    if file_path.lower().endswith('.pdf'):
        with open(file_path, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
            return response
    else:
        return FileResponse(open(file_path, 'rb'))
