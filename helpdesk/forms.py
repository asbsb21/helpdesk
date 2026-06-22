from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Ticket, User


class BootstrapMixin:
    """Добавляет Bootstrap-классы ко всем полям формы."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class SignUpForm(BootstrapMixin, UserCreationForm):
    """Регистрация нового пользователя (роль по умолчанию — клиент)."""

    first_name = forms.CharField(label="Имя", max_length=150, required=True)
    last_name = forms.CharField(label="Фамилия", max_length=150, required=False)
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")


class TicketForm(BootstrapMixin, forms.ModelForm):
    """Создание/редактирование заявки клиентом."""

    class Meta:
        model = Ticket
        fields = ("title", "description", "category", "priority", "tags")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "tags": forms.SelectMultiple(attrs={"size": 4}),
        }


class TicketManageForm(BootstrapMixin, forms.ModelForm):
    """Обработка заявки агентом: статус, приоритет, исполнитель, категория."""

    class Meta:
        model = Ticket
        fields = ("status", "priority", "category", "assignee", "tags")
        widgets = {"tags": forms.SelectMultiple(attrs={"size": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Исполнителем может быть только агент или администратор
        self.fields["assignee"].queryset = User.objects.filter(
            role__in=[User.Role.AGENT, User.Role.ADMIN]
        )


class CommentForm(BootstrapMixin, forms.ModelForm):
    """Комментарий к заявке."""

    class Meta:
        model = Comment
        fields = ("body", "is_internal")
        widgets = {"body": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, is_agent=False, **kwargs):
        super().__init__(*args, **kwargs)
        # Внутренние комментарии доступны только агентам
        if not is_agent:
            self.fields.pop("is_internal")
