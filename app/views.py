from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Box, Contract
from .forms import UserRegisterForm, UserLoginForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import date, timedelta
import calendar
from django.contrib.auth import logout

def index(request):
    return render(request, 'index.html', {'title': 'SelfStorage — Место для ваших вещей'})


def catalog(request):
    boxes_list = Box.objects.all().select_related('section')
    query = request.GET.get('q')
    if query:
        boxes_list = boxes_list.filter(number__icontains=query)
    area = request.GET.get('area')
    if area == '1':
        boxes_list = boxes_list.filter(volume__lte=2)
    elif area == '3':
        boxes_list = boxes_list.filter(volume__gt=2, volume__lte=4)
    elif area == '5':
        boxes_list = boxes_list.filter(volume__gt=4, volume__lte=6)
    elif area == '10':
        boxes_list = boxes_list.filter(volume__gt=6, volume__lte=12)
    elif area == '20':
        boxes_list = boxes_list.filter(volume__gt=12)

    floor = request.GET.get('floor')
    if floor:
        boxes_list = boxes_list.filter(section__id=floor)


    available = request.GET.get('available')
    if available == 'on':
        boxes_list = boxes_list.filter(status='free')

    sort = request.GET.get('sort')
    if sort == 'asc':
        boxes_list = boxes_list.order_by('volume')
    elif sort == 'desc':
        boxes_list = boxes_list.order_by('-volume')
    else:
        boxes_list = boxes_list.order_by('number')
    paginator = Paginator(boxes_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Каталог боксов',
        'page_obj': page_obj,
        'current_sort': sort,
        'current_q': query,
        'current_area': area,
        'current_floor': floor,
        'current_available': available
    }
    return render(request, 'catalog.html', context)


def box_detail(request, box_id):
    box = get_object_or_404(Box, id=box_id)

    term = request.GET.get('term', '1')

    base_price_per_m2 = 1500

    price = float(box.volume) * base_price_per_m2

    if term == '3':
        price = price * 0.95
    elif term == '6':
        price = price * 0.9

    price = int(price)

    return render(request, 'box_detail.html', {
        'title': f'Бокс {box.number}',
        'box': box,
        'current_term': term,
        'price': price
    })


@login_required
def profile(request):
    contracts = Contract.objects.filter(client__user=request.user).select_related('box')
    return render(request, 'profile.html', {'title': 'Личный кабинет', 'contracts': contracts})


def about(request):
    return render(request, 'about.html', {'title': 'О компании'})


def calculator(request):
    items_param = request.GET.get('what', '')
    area_param = request.GET.get('area', '')
    term_param = request.GET.get('term', '')

    recommended_area = 0
    base_price = 0

    if items_param:

        if 'Коробки' in items_param:
            recommended_area += 1
            base_price += 1500
        if 'Мебель' in items_param:
            recommended_area += 3
            base_price += 4500
        if 'Техника' in items_param:
            recommended_area += 2
            base_price += 3000
        if 'Шины' in items_param:
            recommended_area += 1
            base_price += 1500
        if 'Спортинвентарь' in items_param:
            recommended_area += 2
            base_price += 2500
        if 'Другое' in items_param:
            recommended_area += 1
            base_price += 1500

    if area_param and area_param.isdigit():
        recommended_area = int(area_param)
        if base_price == 0:
            base_price = recommended_area * 1500

    if recommended_area == 0:
        recommended_area = 3
        base_price = 4500

    multiplier = 1
    if term_param == '3':
        multiplier = 3
        base_price = base_price * 0.95
    elif term_param == '6':
        multiplier = 6
        base_price = base_price * 0.9

    final_price = int(base_price * multiplier)

    context = {
        'title': 'Калькулятор размера',
        'items_param': items_param,
        'area_param': area_param,
        'term_param': term_param,
        'recommended_area': recommended_area,
        'final_price': final_price,
        'is_prefilled': bool(request.GET)
    }
    return render(request, 'calculator.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            from .models import Client
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect('profile')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form, 'title': 'Регистрация'})


def checkout(request, box_id):
    box = get_object_or_404(Box, id=box_id)
    term = int(request.GET.get('term', 1))

    price_per_month = int(float(box.volume) * 1500)

    if term == 3:
        price_per_month = int(price_per_month * 0.95)
    elif term == 6:
        price_per_month = int(price_per_month * 0.9)

    total_rent = price_per_month * term

    context = {
        'title': 'Оформление бронирования',
        'box': box,
        'term': term,
        'total_rent': total_rent
    }
    return render(request, 'checkout.html', context)


def payment(request, box_id):
    box = get_object_or_404(Box, id=box_id)
    term = int(request.GET.get('term', 1))

    total_param = request.GET.get('total')

    if total_param and total_param.isdigit():
        final_sum = int(total_param)
    else:
        price_per_month = int(float(box.volume) * 1500)
        final_sum = price_per_month * term

    if request.method == 'POST':
        if request.user.is_authenticated:
            start = date.today()
            end = start + timedelta(days=30 * term)

            Contract.objects.create(
                client=request.user.client_profile,
                box=box,
                start_date=start,
                end_date=end,
                total_price=final_sum,
                is_active=True
            )
            box.status = 'busy'
            box.save()
            messages.success(request, 'Оплата прошла успешно!')
            return redirect('profile')
        else:
            return redirect('login')

    return render(request, 'payment.html', {'title': 'Оплата', 'box': box, 'term': term, 'total_rent': final_sum})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                messages.error(request, 'Неверный логин или пароль')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form, 'title': 'Вход'})


def catalog_api(request):
    query = request.GET.get('q', '')
    boxes = Box.objects.filter(status='free')
    if query:
        boxes = boxes.filter(number__icontains=query)

    count = boxes.count()
    boxes = boxes[:20]

    html = render_to_string('includes/box_cards.html', {'page_obj': boxes}, request=request)
    return JsonResponse({'html': html, 'count': count})

@login_required
def profile_data(request):
    return render(request, 'profile_data.html', {'title': 'Личные данные'})

@login_required
def payment_history(request):
    return render(request, 'payment_history.html', {'title': 'Способы оплаты'})


def user_logout(request):
    logout(request)
    return redirect('home')

