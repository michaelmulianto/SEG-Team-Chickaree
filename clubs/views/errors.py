from django.shortcuts import render

def page_not_found_custom(request, exception):
    response = render(request, 'http404ErrorPage.html')
    response.status_code = 404
    return response

def server_error_custom(request):
    response = render(request, 'http500ErrorPage.html')
    response.status_code = 500
    return response
