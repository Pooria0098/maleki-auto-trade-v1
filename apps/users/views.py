from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.reverse import reverse_lazy

from apps.users.models import Profile, ApiStatus
from apps.users.forms import ProfileForm, QuillFieldForm, APIForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView
from apps.users.models import API
from django.contrib import messages


# Create your views here.


@login_required(login_url='/accounts/login-v1/')
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    form = QuillFieldForm(instance=profile)
    if request.method == 'POST':

        if request.POST.get('email'):
            request.user.email = request.POST.get('email')
            request.user.save()

        for attribute, value in request.POST.items():
            if attribute == 'csrfmiddlewaretoken':
                continue

            setattr(profile, attribute, value)
            profile.save()

        messages.success(request, 'Profile updated successfully')
        return redirect(request.META.get('HTTP_REFERER'))

    context = {
        'segment': 'profile',
        'form': form,
        "parent": "Apps",
    }
    return render(request, 'pages/apps/user-profile.html', context)


def upload_avatar(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        profile.avatar = request.FILES.get('avatar')
        profile.save()
        messages.success(request, 'Avatar uploaded successfully')
    return redirect(request.META.get('HTTP_REFERER'))


def change_password(request):
    user = request.user
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        if new_password == confirm_new_password:
            if check_password(request.POST.get('current_password'), user.password):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully')
            else:
                messages.error(request, "Old password doesn't match!")
        else:
            messages.error(request, "Password doesn't match!")

    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/accounts/login-v1/')
def change_mode(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.dark_mode:
        profile.dark_mode = False
    else:
        profile.dark_mode = True

    profile.save()

    return redirect(request.META.get('HTTP_REFERER'))


class APICreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'users/apis/api_create.html'
    model = API
    form_class = APIForm
    success_message = 'Successfully Created'

    def get_success_url(self):
        return reverse_lazy('users:api_list')

    def form_invalid(self, form):
        messages.warning(self.request, form.errors)
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(APICreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(APICreateView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'Api',
            'parent_url': 'users:api_list',
            'segment': 'Create',
        })
        return context


class APIListView(LoginRequiredMixin, ListView):
    template_name = 'users/apis/api_list.html'
    model = API
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super(APIListView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'Api',
            'segment': 'List',
        })
        return context


class APIUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'users/apis/api_create.html'
    model = API
    form_class = APIForm
    success_message = 'Successfully Updated'

    def get_success_url(self):
        return reverse_lazy('users:api_list')

    def form_invalid(self, form):
        messages.warning(self.request, form.errors)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(APIUpdateView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'Api',
            'parent_url': 'users:api_list',
            'segment': 'Update',
        })
        return context


class APIActiveView(LoginRequiredMixin, DeleteView):
    template_name = 'users/apis/api_list.html'
    model = API

    def get_success_url(self):
        return reverse_lazy('users:api_list')

    def form_valid(self, form):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.status = ApiStatus.Active
        self.object.save()
        return HttpResponseRedirect(success_url)


class APIDeActiveView(LoginRequiredMixin, DeleteView):
    template_name = 'users/apis/api_list.html'
    model = API

    def get_success_url(self):
        return reverse_lazy('users:api_list')

    def form_valid(self, form):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.status = ApiStatus.Deactive
        self.object.save()
        return HttpResponseRedirect(success_url)
