from django.shortcuts import render
from django.views.generic import TemplateView


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
class PoliticaCookiesView(TemplateView):
    template_name = 'politica-cookies.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Política de Cookies - Yoursecurescan',
            'last_updated': '05 de junio de 2025',
            'contact_email': 'privacy@yoursecurescan.com'
        })
        return context

