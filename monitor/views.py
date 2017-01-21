from django.shortcuts import render
from django.views.generic import View,TemplateView
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
# Create your views here.
from .login_api import LoginRequiredMixin
try:
    import simplejson as json
except ImportError:
    import json
from client import CeleryClient
from djcelery.admin import PeriodicTaskForm
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy
from djcelery.models import IntervalSchedule,CrontabSchedule,PeriodicTask,TaskState
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib import messages
from django.db import models
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib import admin

class workers(LoginRequiredMixin,View):
    def get(self,request):
        instance=CeleryClient()
        response = instance.workers()
        if not response:
            return HttpResponse(json.dumps([]),content_type="application/json")
        else:
            return HttpResponse(json.dumps(response),content_type="application/json")
    def post(self,request):
        pass
    
class tasks(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.registered_tasks()
        if not response:
            return HttpResponse(json.dumps([]),content_type="application/json")
        else:
            return HttpResponse(json.dumps(response),content_type="application/json")
    def post(self,request):
        pass
    
class active_tasks(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.active_tasks()
        if not response:
            return HttpResponse(json.dumps([]),content_type="application/json")
        else:
            return HttpResponse(json.dumps(response),content_type="application/json")
    def post(self,request):
        pass

class reserved_tasks(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.reserved_tasks()
        if not response:
            return HttpResponse(json.dumps([]),content_type="application/json")
        else:
            return HttpResponse(json.dumps(response),content_type="application/json")
    def post(self,request):
        pass

class active_queues(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.active_queues()
        if not response:
            return HttpResponse(json.dumps([]),content_type="application/json")
        else:
            return HttpResponse(json.dumps(response),content_type="application/json")
    def post(self,request):
        pass

class queues_configuration(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.active_queues()
        return render_to_response('queues_configuration.html',locals())
    def post(self,request):
        pass

class workers_index(LoginRequiredMixin,View):
    def get(self,request):
        import time
        a=time.time()
        instance = CeleryClient()
        b=time.time()
        response = instance.workers() 
        c=time.time()
        #print b - a
        #print c - b
        #print c - a
        #print response
        #from django.utils import translation
        #user_language = 'zh-hans'
        ###user_language = 'en'
        #translation.activate(user_language)
        #request.session[translation.LANGUAGE_SESSION_KEY] = user_language	        
        return render_to_response('workers.html',locals())
    
class registered_tasks_index(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.registered_tasks()
        return render_to_response('registered_tasks.html',locals())

class active_tasks_index(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.active_tasks()
        title = 'Active Tasks'
        action = 'terminate'
        return render_to_response('active_tasks.html',locals())

class reserved_tasks_index(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.reserved_tasks()
        title='Reserved Tasks'
        action = 'revoke'
        return render_to_response('active_tasks.html',locals())

class task_configuration(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.worker_registered_tasks()
        #print response
        return render_to_response('task_configuration.html',locals())

class worker_status(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        stats = instance.worker_stats
        #print stats
        #active_task=instance.active_tasks()
        #reserved_tasks=instance.reserved_tasks()
        revoked_tasks=instance.revoked_tasks()
        #print revoked_tasks
        #scheduled_tasks=instance.scheduled_tasks()
        return render_to_response('worker_status.html',locals())
    
class pool_configuration(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        stats = instance.worker_stats
        return render_to_response('pool_configuration.html',locals())

class operations(LoginRequiredMixin,View):
    def get(self,request):
        command = self.request.GET.get('command','')
        parameter = json.loads(self.request.GET.get('parameter',''))
        #print 'get',self.request.GET
        #print 'command',command
        #print 'parameter',parameter
        instance = CeleryClient()
        response = instance.execute(command, parameter)
        return HttpResponse(json.dumps(response),content_type="application/json")

class periodictaskcreate(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    form_class = PeriodicTaskForm
    template_name = 'periodictaskcreate.html'
    success_url = reverse_lazy('periodictask_list')
    success_message = "%(name)s was created successfully"
    model = PeriodicTask
    def get_form(self, form_class):
        form = super(periodictaskcreate, self).get_form(form_class)
        rel_model = form.Meta.model
        rel = rel_model._meta.get_field('crontab').rel        
        form.fields['crontab'].widget = RelatedFieldWidgetWrapper(form.fields['crontab'].widget, rel, 
                                                                  admin.site, can_add_related=True, can_change_related=True)
        form.fields['interval'].widget = RelatedFieldWidgetWrapper(form.fields['interval'].widget, rel, 
                                                                          admin.site, can_add_related=True, can_change_related=True)        
        return form    

class periodictaskupdate(LoginRequiredMixin,SuccessMessageMixin, UpdateView):
    form_class = PeriodicTaskForm
    template_name = 'periodictaskupdate.html'
    success_url = reverse_lazy('periodictask_list')
    success_message = "%(name)s was updated successfully"
    model = PeriodicTask   
    def get_form(self, form_class):
        form = super(periodictaskupdate, self).get_form(form_class)
        rel_model = form.Meta.model
        rel = rel_model._meta.get_field('crontab').rel        
        form.fields['crontab'].widget = RelatedFieldWidgetWrapper(form.fields['crontab'].widget, rel, 
                                                                  admin.site, can_add_related=True, can_change_related=True)
        form.fields['interval'].widget = RelatedFieldWidgetWrapper(form.fields['interval'].widget, rel, 
                                                                          admin.site, can_add_related=True, can_change_related=True)        
        return form
    
class periodictasklist(LoginRequiredMixin,ListView):
    template_name = 'periodictasklist.html'
    def get_queryset(self):
        return PeriodicTask.objects.all()
    
class periodictaskdetail(LoginRequiredMixin,SuccessMessageMixin, UpdateView):
    form_class = PeriodicTaskForm
    template_name = 'periodictaskdetail.html'
    success_url = reverse_lazy('periodictask_list')
    success_message = "%(name)s was updated successfully"
    model = PeriodicTask

    
class periodictaskdelete(LoginRequiredMixin,DeleteView):
    template_name = 'periodictaskdelete.html'
    model = PeriodicTask
    success_url = reverse_lazy('periodictask_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.add_message(request, messages.INFO, self.object.name + ' was deleted successfully.')
        except Exception,e:
            print e
            messages.add_message(request, messages.ERROR, self.object.name + ' can not deleted because hosts use that ENV!')

        return HttpResponseRedirect(self.get_success_url())
    
class crontabcreate(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    template_name = 'crontabcreate.html'
    success_url = reverse_lazy('crontab_add')
    success_message = "crontab was created successfully"
    model = CrontabSchedule
    fields=['minute','hour','day_of_week','day_of_month','month_of_year']

class intervalcreate(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    template_name = 'intervalcreate.html'
    success_url = reverse_lazy('interval_add')
    success_message = "interval was created successfully"
    model = IntervalSchedule
    fields=['every','period']
  
class taskstatedetail(LoginRequiredMixin,DetailView):
    model = TaskState
    template_name = 'taskstatedetail.html'