from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Box, Contract


def index(request):
    return render(request, 'index.html', {'title': 'SelfStorage — Место для ваших вещей'})


def catalog(request):
    boxes_list = Box.objects.filter(status='free').select_related('section')

    paginator = Paginator(boxes_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'catalog.html', {'title': 'Каталог боксов', 'page_obj': page_obj})


def box_detail(request, box_id):
    box = get_object_or_404(Box, id=box_id)
    return render(request, 'box_detail.html', {'title': f'Бокс {box.number}', 'box': box})


def profile(request):
    contracts = Contract.objects.select_related('box', 'client__user').all()
    return render(request, 'profile.html', {'title': 'Личный кабинет', 'contracts': contracts})


def about(request):
    return render(request, 'about.html', {'title': 'О компании'})

def calculator(request):
    return render(request, 'calculator.html', {'title': 'Калькулятор размера'})