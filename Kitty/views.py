from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import User, Kitty, Adoption
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test


# Create your views here.


def homepage(request):
    kitties = Kitty.objects.all()
    return render(request, 'Kitty/homepage.html', {'kitties': kitties})

def about(request):
    return render(request, 'Kitty/about.html')


def contact(request):
    if request.method == 'POST':
        # Get the data from the form
        email = request.POST.get('email')
        title = request.POST.get('title')
        description = request.POST.get('description')

        # Prepare the email content
        subject = f"Message from {email}: {title}"
        message = f"Message:\n\n{description}\n\nFrom: {email}"
        from_email = email  # Use the user's email as the sender
        recipient_list = ['delusionalmuscle@gmail.com']  # The company's email address (you'll set this in settings.py)

        try:
            # Send the email
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            return HttpResponse('Message sent successfully!', status=200)
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)
    else:
        return render(request, 'Kitty/contact_us.html')



def support(request):
    return render(request, 'Kitty/support_us.html')



def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validation
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'Kitty/sign_up.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'Kitty/sign_up.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'Kitty/sign_up.html')

        # Create User
        user = User(
            username=username,
            email=email,
            password=make_password(password1),  # Hash the password for security
        )
        user.save()

        messages.success(request, "Your account has been created successfully!")
        return redirect('login')

    return render(request, 'Kitty/sign_up.html')



# Custom login view
@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if credentials are provided
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'Kitty/login.html')

        try:
            # Authenticate the user using Django's built-in authentication system
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                
                # Store additional session data if needed
                request.session['user_id'] = user.id
                request.session['user_email'] = user.email  # Assumes your User model has an email field

                # Redirect to a role-based page or home
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('home')  # Replace 'home' with the desired route

            else:
                messages.error(request, "Invalid username or password. Please try again.")
        
        except Exception as e:
            # Catch unexpected errors and log them (if logging is set up)
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    
    # Render the login page if the method is not POST or login fails
    return render(request, 'Kitty/login.html')

def user_logout(request):
    logout(request)  # Log out the user
    return redirect('home')  # Redirect to the home page after logging out

@login_required
def user_profile(request):
    user = request.user  # Get the logged-in user
    if request.method == 'POST':
        # Handle form data and update user information
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        picture = request.FILES.get('picture')
        no_tel = request.POST.get('no_tel')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        date_of_birth = request.POST.get('date_of_birth')
        ic_no = request.POST.get('ic_no')

        # Manually update the user data
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.no_tel = no_tel
        user.gender = gender
        user.address = address
        user.date_of_birth = date_of_birth
        user.ic_no = ic_no

        if picture:
            # If a new profile picture is uploaded
            user.picture = picture


        print("Saving user data...")
        user.save()  # Save the updated user data

        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('view_profile')  # Redirect back to the profile page after saving

    return render(request, 'Kitty/user_profile.html', {'user': user})

@login_required
def view_profile(request):
    user = request.user  # Get the logged-in user
    return render(request, 'Kitty/view_profile.html', {'user': user})


@login_required
def adopt_kitty(request, kitty_id):
    kitty = get_object_or_404(Kitty, id=kitty_id)
    user=request.user._wrapped
    
    if request.method == "POST":
        # Generate a unique adoption ID
        adopt_id = get_random_string(length=20)

        # Create the adoption record
        adoption = Adoption.objects.create(
            user=user,
            kitty=kitty,
            adopt_id=adopt_id,
            status='PENDING',  # Default status is 'PENDING'
        )
        
        # Redirect to the adoption details page (optional, adjust URL as needed)
        return redirect('adopt_details', adopt_id=adoption.adopt_id)

    return render(request, 'Kitty/adopt.html', {'kitty': kitty})


@login_required
def adopt_details(request, adopt_id):
    adoption = get_object_or_404(Adoption, adopt_id=adopt_id)
    return render(request, 'Kitty/adopt_details.html', {'adoption': adoption})



def is_admin(user):
    return user.is_superuser  # Check if the user is a superuser

@user_passes_test(is_admin, login_url='login') 
def add_kitty(request):
    if request.method == 'POST':
        # Retrieve form data
        name = request.POST.get('name')
        species = request.POST.get('species')
        age = request.POST.get('age')
        detail = request.POST.get('detail')
        history = request.POST.get('history', '')  # History can be optional
        date_of_birth = request.POST.get('date_of_birth')
        picture = request.FILES.get('picture')  # Handling the file upload

        # Validate the date format for date_of_birth
        try:
            date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            return redirect('add_kitty')  # Redirect back to the form if validation fails

        # Create the Kitty object
        try:
            kitty = Kitty(
                name=name,
                species=species,
                age=age,
                detail=detail,
                history=history,
                date_of_birth=date_of_birth,
                picture=picture
            )
            kitty.save()
            messages.success(request, 'Kitty added successfully!')
            return redirect('home')  # Redirect to the home page after saving
        except ValidationError as e:
            messages.error(request, f'Error: {e}')
            return redirect('add_kitty')  # Redirect back to the form if there's a validation error

    return render(request, 'Kitty/add_kitty.html')
