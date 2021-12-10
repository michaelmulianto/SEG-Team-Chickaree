from django.shortcuts import render

def page_not_found_custom(request, exception):
    context = {}
    return render(request, 'http404ErrorPage.html')

def server_error_custom(request):
    return render(request, 'http500ErrorPage.html')
