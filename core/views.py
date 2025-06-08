from django.shortcuts import render

def faq_view(request):
    return render(request, 'core/faq.html')

def privacy_policy_view(request):
    return render(request, 'core/privacy.html')

def terms_of_use_view(request):

    return render(request, 'core/terms_of_use.html')
