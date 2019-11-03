from django import forms
from django.contrib import auth
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'}))
    password = forms.CharField(label='密码',
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}))

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = auth.authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError("用户名或密码不正确")
        self.cleaned_data['user'] = user


class RegisterForm(forms.Form):
    username = forms.CharField(label='用户名',
                               max_length=20,
                               min_length=3,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入3-20位用户名'}))
    email = forms.EmailField(label='邮箱',
                             max_length=40,
                             min_length=6,
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'}))
    verification_code = forms.CharField(label='邮箱验证码', required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control',
                                                                      'placeholder': '点击“发送验证码”发送到邮箱'}))
    password = forms.CharField(label='密码',
                               max_length=20,
                               min_length=6,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入6-20位密码'}))
    password_again = forms.CharField(label='密码确认',
                                     widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入密码'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("用户名已被占用")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已被注册')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '')
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        forget_password_code = self.request.session.get('register_code', '')
        if forget_password_code == '':
            raise forms.ValidationError('请点击“发送验证码”发送到邮箱')
        if forget_password_code != verification_code:
            raise forms.ValidationError('验证失败')
        return verification_code

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('两次输入的密码不一致')
        return password_again


class ChangeAliasForm(forms.Form):
    alias_new = forms.CharField(label='新的昵称', max_length=20,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入新的昵称'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        # 用户验证
        if not self.user.is_authenticated:
            raise forms.ValidationError('用户尚未登录')
        return self.cleaned_data

    def clean_alias_new(self):
        alias_new = self.cleaned_data.get('alias_new', '').strip()
        if alias_new == '':
            raise forms.ValidationError('昵称不能为空')
        return alias_new


class BindEmailForm(forms.Form):
    email = forms.EmailField(label='邮箱',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'}))

    verification_code = forms.CharField(label='验证码', required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        # 用户验证
        if not self.request.user.is_authenticated:
            raise forms.ValidationError('用户尚未登录')
        # 是否已经绑定邮箱
        if self.request.user.email != '':
            raise forms.ValidationError('用户已绑定邮箱')
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email == '':
            raise forms.ValidationError('邮箱不能为空')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被绑定')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '')
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        bind_email_code = self.request.session.get('bind_email_code', '')
        if bind_email_code == '':
            raise forms.ValidationError('请点击“发送验证码”发送到邮箱')
        if bind_email_code != verification_code:
            raise forms.ValidationError('验证失败')
        return verification_code


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='旧的密码',
                                   widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入旧的密码'}))
    new_password = forms.CharField(label='新的密码',
                                   max_length=20,
                                   min_length=6,
                                   widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入新的6-20位密码'}))
    new_password_again = forms.CharField(label='新的密码确认',
                                         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入新的密码'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        if new_password != new_password_again:
            raise forms.ValidationError('两次输入的密码不一致')
        return self.cleaned_data

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('旧的密码错误')
        return old_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password', '')
        if new_password == '':
            raise forms.ValidationError('密码不能为空')
        return new_password


class ForgetPasswordForm(forms.Form):
    email = forms.EmailField(label='邮箱',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入绑定的邮箱'}))
    verification_code = forms.CharField(label='验证码', required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}))
    new_password = forms.CharField(label='新的密码',
                                   max_length=20,
                                   min_length=6,
                                   widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入新的6-20位密码'}))
    new_password_again = forms.CharField(label='新的密码确认',
                                         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入新的密码'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("绑定此邮箱的用户不存在")
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '')
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        forget_password_code = self.request.session.get('forget_password_code', '')
        if forget_password_code == '':
            raise forms.ValidationError('请点击“发送验证码”发送到邮箱')
        if forget_password_code != verification_code:
            raise forms.ValidationError('验证失败')
        return verification_code

