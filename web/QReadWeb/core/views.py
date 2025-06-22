from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class Index(View):
    def get(self, request):
        return render(request, 'core/index.html')
    
class Dashboard(View, LoginRequiredMixin):
    def get(self, request):
        return render(request, 'core/dashboard.html')