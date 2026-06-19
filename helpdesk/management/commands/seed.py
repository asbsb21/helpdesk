"""Заполнение базы тестовыми данными: справочники, аккаунты и примеры заявок.

Запуск:  python manage.py seed
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from helpdesk.models import Category, Comment, Priority, Status, Tag, Ticket, User


class Command(BaseCommand):
    help = "Заполняет базу тестовыми данными (справочники, пользователи, заявки)."

    @transaction.atomic
    def handle(self, *args, **options):
        # --- Справочники ---
        statuses = {}
        for i, (name, closed) in enumerate(
            [("Новая", False), ("В работе", False), ("Ожидание", False),
             ("Решена", True), ("Закрыта", True)]
        ):
            statuses[name], _ = Status.objects.get_or_create(
                name=name, defaults={"order": i, "is_closed": closed}
            )

        priorities = {}
        for i, name in enumerate(["Низкий", "Обычный", "Высокий", "Срочный"]):
            priorities[name], _ = Priority.objects.get_or_create(name=name, defaults={"weight": i})

        categories = {}
        for name in ["Оборудование", "Программное обеспечение", "Доступы", "Прочее"]:
            categories[name], _ = Category.objects.get_or_create(name=name)

        tags = {}
        for name in ["срочно", "повтор", "сеть", "1С"]:
            tags[name], _ = Tag.objects.get_or_create(name=name)

        # --- Пользователи (роли) ---
        def make_user(username, password, role, first, last, email, **extra):
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"role": role, "first_name": first, "last_name": last,
                          "email": email, **extra},
            )
            if created:
                user.set_password(password)
                user.save()
            return user

        admin = make_user("admin", "admin12345", User.Role.ADMIN, "Анна", "Администратова",
                          "admin@example.com", is_staff=True, is_superuser=True)
        agent = make_user("agent", "agent12345", User.Role.AGENT, "Игорь", "Агентов",
                          "agent@example.com", is_staff=True)
        agent2 = make_user("agent2", "agent12345", User.Role.AGENT, "Олег", "Поддержкин",
                           "agent2@example.com", is_staff=True)
        client = make_user("client", "client12345", User.Role.CLIENT, "Пётр", "Клиентов",
                           "client@example.com")
        client2 = make_user("client2", "client12345", User.Role.CLIENT, "Мария", "Заявкина",
                            "client2@example.com")

        # --- Примеры заявок ---
        if Ticket.objects.exists():
            self.stdout.write(self.style.WARNING("Заявки уже есть — пропускаю создание примеров."))
        else:
            samples = [
                (client, "Не печатает принтер", "Принтер в кабинете 305 не реагирует на печать.",
                 categories["Оборудование"], priorities["Высокий"], statuses["В работе"], agent, ["сеть"]),
                (client, "Нет доступа к 1С", "При входе в 1С пишет «неверный логин».",
                 categories["Доступы"], priorities["Срочный"], statuses["Новая"], None, ["1С", "срочно"]),
                (client2, "Обновить Word", "Просьба обновить пакет Office до последней версии.",
                 categories["Программное обеспечение"], priorities["Низкий"], statuses["Ожидание"], agent2, []),
                (client2, "Медленно работает интернет", "Страницы открываются по 30 секунд.",
                 categories["Оборудование"], priorities["Обычный"], statuses["Решена"], agent, ["сеть", "повтор"]),
            ]
            for author, title, desc, cat, prio, status, assignee, tag_names in samples:
                ticket = Ticket.objects.create(
                    title=title, description=desc, author=author, category=cat,
                    priority=prio, status=status, assignee=assignee,
                )
                if tag_names:
                    ticket.tags.set([tags[t] for t in tag_names])
                Comment.objects.create(
                    ticket=ticket, author=assignee or agent,
                    body="Принято в работу, разбираемся.", is_internal=False,
                )

        self.stdout.write(self.style.SUCCESS("Готово! Тестовые данные загружены."))
        self.stdout.write("Аккаунты для входа:")
        self.stdout.write("  admin  / admin12345   (Администратор)")
        self.stdout.write("  agent  / agent12345   (Агент)")
        self.stdout.write("  client / client12345  (Клиент)")
