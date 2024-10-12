from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView

from home.home_forms.api import APIForm
from home.models import API
from django.contrib import messages


class APICreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'home/api/api_create.html'
    model = API
    form_class = APIForm
    # success_url = reverse_lazy('profile')
    context_object_name = 'api_form'

    def form_invalid(self, form):
        messages.warning(self.request, form.errors)
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(APICreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['parent'] = 'form_components'
        initial['segment'] = 'form_validation'
        return initial