from django.shortcuts import render
from django.template.context import RequestContext
from django.views.generic import TemplateView
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponseServerError, HttpResponseNotFound

# class Http404ErrorHandler(TemplateView):
#     """ Render 404 Error Template"""

#     error_code = 404
#     template_name = 'http404ErrorPage.html'

#     def dispatch(self, request, *args, **kwargs):
#         return self.get(request, *args, **kwargs)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['error_code'] = self.error_code
#         return context

#     def render_to_response(self, context, **response_kwargs):
#         response_kwargs = response_kwargs or {}
#         response_kwargs.update(status = self.error_code)
#         return super().render_to_response(context, **response_kwargs)

def page_not_found_custom(request, exception):
    response = render(request, 'http404ErrorPage.html')
    response.status_code = 404
    return response

def server_error_custom(request):
    response = render(request, 'http500ErrorPage.html')
    response.status_code = 500
    return response
