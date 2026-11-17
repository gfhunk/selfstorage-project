from django.shortcuts import render

def index(request):
    context = {
        'title': 'SelfStorage — Место для ваших вещей'
    }
    return render(request, 'index.html', context)