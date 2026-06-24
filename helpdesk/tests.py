from django.test import TestCase
from django.urls import reverse

from .models import Category, Priority, Status, Ticket, User


class BaseData(TestCase):
    """Общие тестовые данные."""

    @classmethod
    def setUpTestData(cls):
        cls.new = Status.objects.create(name="Новая", order=0)
        cls.closed = Status.objects.create(name="Закрыта", order=5, is_closed=True)
        cls.prio = Priority.objects.create(name="Обычный", weight=1)
        cls.cat = Category.objects.create(name="Прочее")
        cls.client_user = User.objects.create_user("client", password="pass12345", role=User.Role.CLIENT)
        cls.other_user = User.objects.create_user("other", password="pass12345", role=User.Role.CLIENT)
        cls.agent = User.objects.create_user("agent", password="pass12345", role=User.Role.AGENT)

    def make_ticket(self, author):
        return Ticket.objects.create(
            title="Тест", description="Описание", author=author,
            category=self.cat, status=self.new, priority=self.prio,
        )


class ModelTests(BaseData):
    def test_password_is_hashed(self):
        """Пароль не хранится в открытом виде (защита данных)."""
        self.assertNotEqual(self.client_user.password, "pass12345")
        self.assertTrue(self.client_user.check_password("pass12345"))

    def test_role_helpers(self):
        self.assertTrue(self.agent.is_agent)
        self.assertFalse(self.client_user.is_agent)

    def test_ticket_str(self):
        ticket = self.make_ticket(self.client_user)
        self.assertIn("Тест", str(ticket))


class AccessControlTests(BaseData):
    def test_login_required(self):
        resp = self.client.get(reverse("ticket_list"))
        self.assertEqual(resp.status_code, 302)  # редирект на логин

    def test_client_sees_only_own_tickets(self):
        self.make_ticket(self.client_user)
        self.make_ticket(self.other_user)
        self.client.login(username="client", password="pass12345")
        resp = self.client.get(reverse("ticket_list"))
        self.assertEqual(len(resp.context["tickets"]), 1)

    def test_agent_sees_all_tickets(self):
        self.make_ticket(self.client_user)
        self.make_ticket(self.other_user)
        self.client.login(username="agent", password="pass12345")
        resp = self.client.get(reverse("ticket_list"))
        self.assertEqual(len(resp.context["tickets"]), 2)

    def test_client_cannot_open_foreign_ticket(self):
        ticket = self.make_ticket(self.other_user)
        self.client.login(username="client", password="pass12345")
        resp = self.client.get(reverse("ticket_detail", args=[ticket.pk]))
        self.assertEqual(resp.status_code, 403)

    def test_client_cannot_manage_ticket(self):
        ticket = self.make_ticket(self.client_user)
        self.client.login(username="client", password="pass12345")
        resp = self.client.post(reverse("ticket_manage", args=[ticket.pk]),
                                {"status": self.new.pk, "priority": self.prio.pk,
                                 "category": self.cat.pk})
        self.assertEqual(resp.status_code, 403)


class WorkflowTests(BaseData):
    def test_create_ticket(self):
        self.client.login(username="client", password="pass12345")
        resp = self.client.post(reverse("ticket_create"), {
            "title": "Новая проблема", "description": "Текст",
            "category": self.cat.pk, "priority": self.prio.pk,
        })
        self.assertEqual(Ticket.objects.count(), 1)
        ticket = Ticket.objects.first()
        self.assertEqual(ticket.author, self.client_user)
        self.assertEqual(ticket.status, self.new)  # статус выставлен автоматически

    def test_agent_closes_ticket_sets_closed_at(self):
        ticket = self.make_ticket(self.client_user)
        self.client.login(username="agent", password="pass12345")
        self.client.post(reverse("ticket_manage", args=[ticket.pk]), {
            "status": self.closed.pk, "priority": self.prio.pk, "category": self.cat.pk,
        })
        ticket.refresh_from_db()
        self.assertIsNotNone(ticket.closed_at)
