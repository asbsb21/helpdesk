from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, SignUpForm, TicketForm, TicketManageForm
from .models import Category, Status, Ticket


def register(request):
    """Регистрация нового пользователя."""
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно. Добро пожаловать!")
            return redirect("ticket_list")
    else:
        form = SignUpForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def ticket_list(request):
    """Список заявок: клиент видит свои, агент/админ — все."""
    tickets = Ticket.objects.select_related(
        "author", "assignee", "category", "status", "priority"
    )
    if not request.user.is_agent:
        tickets = tickets.filter(author=request.user)

    # Фильтры
    status_id = request.GET.get("status")
    category_id = request.GET.get("category")
    query = request.GET.get("q", "").strip()
    if status_id:
        tickets = tickets.filter(status_id=status_id)
    if category_id:
        tickets = tickets.filter(category_id=category_id)
    if query:
        tickets = tickets.filter(Q(title__icontains=query) | Q(description__icontains=query))

    context = {
        "tickets": tickets,
        "statuses": Status.objects.all(),
        "categories": Category.objects.all(),
        "current_status": status_id,
        "current_category": category_id,
        "query": query,
    }
    return render(request, "helpdesk/ticket_list.html", context)


@login_required
def ticket_detail(request, pk):
    """Карточка заявки: просмотр, переписка."""
    ticket = get_object_or_404(
        Ticket.objects.select_related("author", "assignee", "category", "status", "priority"),
        pk=pk,
    )
    # Клиент может смотреть только свои заявки
    if not request.user.is_agent and ticket.author != request.user:
        raise PermissionDenied("У вас нет доступа к этой заявке.")

    # Внутренние комментарии видны только агентам
    comments = ticket.comments.select_related("author")
    if not request.user.is_agent:
        comments = comments.filter(is_internal=False)

    if request.method == "POST":
        comment_form = CommentForm(request.POST, is_agent=request.user.is_agent)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            messages.success(request, "Комментарий добавлен.")
            return redirect("ticket_detail", pk=ticket.pk)
    else:
        comment_form = CommentForm(is_agent=request.user.is_agent)

    manage_form = TicketManageForm(instance=ticket) if request.user.is_agent else None

    context = {
        "ticket": ticket,
        "comments": comments,
        "comment_form": comment_form,
        "manage_form": manage_form,
    }
    return render(request, "helpdesk/ticket_detail.html", context)


@login_required
def ticket_create(request):
    """Создание заявки (доступно всем ролям)."""
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.author = request.user
            ticket.status = Status.objects.order_by("order").first()
            ticket.save()
            form.save_m2m()
            messages.success(request, f"Заявка #{ticket.pk} создана.")
            return redirect("ticket_detail", pk=ticket.pk)
    else:
        form = TicketForm()
    return render(request, "helpdesk/ticket_form.html", {"form": form, "title": "Новая заявка"})


@login_required
def ticket_manage(request, pk):
    """Обработка заявки агентом: статус, приоритет, исполнитель."""
    ticket = get_object_or_404(Ticket, pk=pk)
    if not request.user.is_agent:
        raise PermissionDenied("Обработка заявок доступна только сотрудникам поддержки.")

    if request.method == "POST":
        form = TicketManageForm(request.POST, instance=ticket)
        if form.is_valid():
            updated = form.save(commit=False)
            # Фиксируем дату закрытия при переходе в закрывающий статус
            if updated.status.is_closed and ticket.closed_at is None:
                updated.closed_at = timezone.now()
            elif not updated.status.is_closed:
                updated.closed_at = None
            updated.save()
            form.save_m2m()
            messages.success(request, "Заявка обновлена.")
    return redirect("ticket_detail", pk=ticket.pk)
