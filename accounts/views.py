from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from agent.models import AIInstruction
from accounts.models import UserProfile

def login_view(request):

    if request.method == "POST":

        username = request.POST["username"]

        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)

            return redirect("/")

        return render(
            request,
            "registration/login.html",
            {"error":"Invalid username or password"}
        )

    return render(request,"registration/login.html")


def logout_view(request):

    logout(request)

    return redirect("login")


def register(request):

    if request.method == "POST":

        User.objects.create_user(

            username=request.POST["username"],

            email=request.POST["email"],

            password=request.POST["password"]

        )

        return redirect("login")

    return render(request,"registration/register.html")

@login_required
def change_password(request):

    if request.method == "POST":

        current_password = request.POST.get("old_password", "").strip()
        new_password = request.POST.get("new_password1", "").strip()
        confirm_password = request.POST.get("new_password2", "").strip()

        # Check current password
        if not request.user.check_password(current_password):

            messages.error(
                request,
                "Current password is incorrect."
            )

            return render(request, "registration/change_password.html")

        # Check password match
        if new_password != confirm_password:

            messages.error(
                request,
                "New password and confirm password do not match."
            )

            return render(request, "registration/change_password.html")

        # Check minimum length
        if len(new_password) < 8:

            messages.error(
                request,
                "Password must be at least 8 characters long."
            )

            return render(request, "registration/change_password.html")

        # Check same password
        if current_password == new_password:

            messages.error(
                request,
                "New password cannot be the same as the current password."
            )

            return render(request, "registration/change_password.html")

        # Update password
        request.user.set_password(new_password)
        request.user.save()

        # Keep user logged in
        update_session_auth_hash(
            request,
            request.user
        )

        messages.success(
            request,
            "Password changed successfully."
        )

        return redirect("profile")

    return render(
        request,
        "registration/change_password.html"
    )



@login_required
def profile(request):

    assistants = AIInstruction.objects.all()

    profile, _ = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        assistant_id = request.POST.get("assistant")

        profile.assistant_id = assistant_id
        profile.save()

        messages.success(
            request,
            "Preferred assistant updated successfully."
        )

        return redirect("profile")

    return render(
        request,
        "registration/profile.html",
        {
            "assistants": assistants,
            "current_assistant": profile.assistant
        }
    )