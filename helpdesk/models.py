from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """Пользователь системы с ролью (клиент / агент / администратор)."""

    class Role(models.TextChoices):
        CLIENT = "client", "Клиент"
        AGENT = "agent", "Агент"
        ADMIN = "admin", "Администратор"

    role = models.CharField("Роль", max_length=10, choices=Role.choices, default=Role.CLIENT)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    @property
    def is_agent(self):
        """Агент или администратор — видит и обрабатывает все заявки."""
        return self.role in (self.Role.AGENT, self.Role.ADMIN)

    @property
    def is_administrator(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return self.get_full_name() or self.username


class Category(models.Model):
    """Категория заявки (Оборудование, ПО, Доступы, Прочее)."""

    name = models.CharField("Название", max_length=100, unique=True)
    description = models.CharField("Описание", max_length=255, blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Status(models.Model):
    """Статус заявки (Новая, В работе, Ожидание, Решена, Закрыта)."""

    name = models.CharField("Название", max_length=50, unique=True)
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_closed = models.BooleanField("Закрывающий статус", default=False)

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ["order"]

    def __str__(self):
        return self.name


class Priority(models.Model):
    """Приоритет заявки (Низкий, Обычный, Высокий, Срочный)."""

    name = models.CharField("Название", max_length=50, unique=True)
    weight = models.PositiveSmallIntegerField("Вес", default=0)

    class Meta:
        verbose_name = "Приоритет"
        verbose_name_plural = "Приоритеты"
        ordering = ["-weight"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Метка для классификации заявок (связь многие-ко-многим)."""

    name = models.CharField("Название", max_length=50, unique=True)

    class Meta:
        verbose_name = "Метка"
        verbose_name_plural = "Метки"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ticket(models.Model):
    """Заявка в службу поддержки."""

    title = models.CharField("Тема", max_length=200)
    description = models.TextField("Описание")
    author = models.ForeignKey(
        User, verbose_name="Автор", on_delete=models.CASCADE, related_name="created_tickets"
    )
    assignee = models.ForeignKey(
        User,
        verbose_name="Исполнитель",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.PROTECT)
    status = models.ForeignKey(Status, verbose_name="Статус", on_delete=models.PROTECT)
    priority = models.ForeignKey(Priority, verbose_name="Приоритет", on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, verbose_name="Метки", blank=True, related_name="tickets")
    created_at = models.DateTimeField("Создана", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлена", auto_now=True)
    closed_at = models.DateTimeField("Закрыта", null=True, blank=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} {self.title}"

    def get_absolute_url(self):
        return reverse("ticket_detail", args=[self.pk])


class Comment(models.Model):
    """Комментарий (переписка) по заявке."""

    ticket = models.ForeignKey(
        Ticket, verbose_name="Заявка", on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE)
    body = models.TextField("Текст")
    is_internal = models.BooleanField("Внутренний (виден только агентам)", default=False)
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]

    def __str__(self):
        return f"Комментарий к #{self.ticket_id}"
