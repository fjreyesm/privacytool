from django.shortcuts import render


def faq_view(request):
    return render(request, 'faq.html')

def privacy_policy_view(request):
    return render(request, 'privacy_policy.html')

def terms_of_use_view(request):
        context = {
        'title': 'Términos de Uso',
        'last_updated': '8 de junio de 2025'
    }
        return render(request, 'terms_of_use.html',context)
