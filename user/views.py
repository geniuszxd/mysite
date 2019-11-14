import string
import random
import time
from django.shortcuts import render, redirect
from django.contrib import auth
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from .forms import LoginForm, RegisterForm, ChangeAliasForm, BindEmailForm, ChangePasswordForm, ForgetPasswordForm
from .models import Profile


def login(request):
    # username = request.POST.get('username', '')
    # password = request.POST.get('password', '')
    # referer = request.META.get('HTTP_REFERER', reverse('home'))
    # user = auth.authenticate(request, username=username, password=password)
    # if user is not None:
    #     auth.login(request, user)
    #     return redirect(referer)
    # else:
    #     # Return an 'invalid login' error message.
    #     return render(request, "error.html", {'message': '用户名或密码错误，请重新登录。', 'backward': referer})

    redirect_url = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(redirect_url)
    else:  # GET
        login_form = LoginForm()
    context = {'form': login_form,
               'page_title': '登录',
               'form_title': '登录',
               'submit_text': '登录',
               'back_url': redirect_url,
               'user_enabled': False,
               'visitor_enabled': True}
    return render(request, 'user/login.html', context)


def register(request):
    redirect_url = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        register_form = RegisterForm(request.POST, request=request)
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            email = register_form.cleaned_data['email']
            password = register_form.cleaned_data['password']
            user = User.objects.create_user(username, email, password)
            user.save()
            auth.login(request, user)
            # 清除session
            del request.session['register_code']
            return redirect(redirect_url)
    else:  # GET
        register_form = RegisterForm()
    context = {'form': register_form,
               'page_title': '注册',
               'form_title': '注册',
               'submit_text': '注册',
               'back_url': redirect_url,
               'user_enabled': False,
               'visitor_enabled': True,
               'code_for': 'register_code'}
    return render(request, 'user/email_verification.html', context)


def login_for_medal(request):
    login_form = LoginForm(request.POST)
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data = {'status': 'SUCCESS'}
    else:
        data = {'status': 'ERROR'}
    return JsonResponse(data)


def profile(request):
    return render(request, 'user/profile.html', {})


def logout(request):
    auth.logout(request)
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    return redirect(referer)


def change_alias(request):
    redirect_url = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = ChangeAliasForm(request.POST, user=request.user)
        if form.is_valid():
            alias_new = form.cleaned_data["alias_new"]
            user_profile, _ = Profile.objects.get_or_create(user=request.user)
            user_profile.alias = alias_new
            user_profile.save()
            return redirect(redirect_url)
    else:  # GET
        form = ChangeAliasForm()
    context = {'form': form,
               'page_title': '修改昵称',
               'form_title': '修改昵称',
               'submit_text': '修改',
               'back_url': redirect_url,
               'user_enabled': True,
               'visitor_enabled': False}
    return render(request, 'form.html', context)


def bind_email(request):
    redirect_url = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            # 清除session
            del request.session['bind_email_code']
            return redirect(redirect_url)
    else:  # GET
        form = BindEmailForm()
    context = {'form': form,
               'page_title': '绑定邮箱',
               'form_title': '绑定邮箱',
               'submit_text': '绑定',
               'back_url': redirect_url,
               'user_enabled': True,
               'visitor_enabled': False,
               'code_for': 'bind_email_code'}
    return render(request, 'user/email_verification.html', context)


def send_verification_code(request):
    email = request.GET.get('email', '')
    code_for = request.GET.get('code_for', '')
    if email == '' or code_for == '':
        return JsonResponse({'status': 'ERROR'})

    # 验证时间
    now = int(time.time())
    send_code_time = request.session.get('send_code_time', 0)
    if send_code_time != 0 and now - send_code_time < 30:
        return JsonResponse({'status': 'ERROR'})
    request.session['send_code_time'] = send_code_time

    # 生成验证码
    true_code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
    request.session[code_for] = true_code  # 默认失效两周

    # 发送邮件
    send_mail(
        '绑定邮箱',  # 标题
        '验证码：' + true_code,  # 内容
        'zhuangxiaodong@foxmail.com',  # From
        [email],  # To
        fail_silently=False,
    )
    return JsonResponse({'status': 'SUCCESS'})


def change_password(request):
    redirect_url = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()
            return redirect(redirect_url)
    else:  # GET
        form = ChangePasswordForm()
    context = {'form': form,
               'page_title': '修改密码',
               'form_title': '修改密码',
               'submit_text': '修改',
               'back_url': redirect_url,
               'user_enabled': True,
               'visitor_enabled': False}
    return render(request, 'form.html', context)


def forget_password(request):
    redirect_url = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            # 清除session
            del request.session['forget_password_code']
            return redirect(redirect_url)
    else:  # GET
        form = ForgetPasswordForm()
    context = {'form': form,
               'page_title': '重置密码',
               'form_title': '重置密码',
               'submit_text': '重置',
               'back_url': redirect_url,
               'user_enabled': False,
               'visitor_enabled': True,
               'code_for': 'forget_password_code'}
    return render(request, 'user/email_verification.html', context)

