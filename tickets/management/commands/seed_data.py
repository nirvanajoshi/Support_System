from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tickets.models import Ticket, TicketReply
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = "Seed the database with a test user, sample tickets, and replies"

    def handle(self, *args, **options):
        now = timezone.now()

        # ── Create test user ──────────────────────────────────────────
        user, created = User.objects.get_or_create(
            username="Damodar_Joshi",
            defaults={"email": "damodar.joshi@example.com"},
        )
        if created:
            user.set_password("demo12345")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user: {user.username}"))
        else:
            user.set_password("demo12345")
            user.save()
            self.stdout.write(f"User '{user.username}' already exists — password reset to demo12345")

        # ── Create a staff user for replies ───────────────────────────
        staff, _ = User.objects.get_or_create(
            username="Support_Agent",
            defaults={"email": "support@helpdesk.local"},
        )
        if not staff.is_staff:
            staff.is_staff = True
            staff.set_password("support123")
            staff.save()
        self.stdout.write(f"Staff user: {staff.username}")

        # ── Helper to set created_at (bypasses auto_now_add) ──────────
        def set_ticket_time(ticket, dt):
            Ticket.objects.filter(pk=ticket.pk).update(created_at=dt)

        def set_reply_time(reply, dt):
            TicketReply.objects.filter(pk=reply.pk).update(created_at=dt)

        # ── Sample Ticket 1 (Open) ────────────────────────────────────
        ticket1, created = Ticket.objects.get_or_create(
            subject="Cannot access my account dashboard",
            defaults={
                "user": user,
                "description": (
                    "Hi, I've been trying to log in to my account for the past two days, "
                    "but every time I enter my credentials, I get a 'Service Unavailable' "
                    "error on the dashboard page. Other pages seem to load fine.\n\n"
                    "I've tried clearing my cache and using a different browser, but the "
                    "issue persists. Can you please look into this?\n\n"
                    "Thanks,\nDamodar"
                ),
                "priority": "high",
                "status": "open",
            },
        )
        t1_created_at = now - timedelta(days=2, hours=3)
        if created:
            set_ticket_time(ticket1, t1_created_at)
            self.stdout.write(self.style.SUCCESS(f"Created ticket: {ticket1.subject}"))
        else:
            self.stdout.write(f"Ticket '{ticket1.subject}' already exists")

        # ── Sample Ticket 2 (In Progress) ─────────────────────────────
        ticket2, created = Ticket.objects.get_or_create(
            subject="Feature request: Dark mode support",
            defaults={
                "user": user,
                "description": (
                    "It would be great if the application could support a dark mode theme. "
                    "I work late hours and the bright interface strains my eyes.\n\n"
                    "A simple toggle in the settings page would be perfect. Many modern "
                    "applications support this now and it's become an expected feature."
                ),
                "priority": "low",
                "status": "in_progress",
            },
        )
        t2_created_at = now - timedelta(days=5, hours=12)
        if created:
            set_ticket_time(ticket2, t2_created_at)
            self.stdout.write(self.style.SUCCESS(f"Created ticket: {ticket2.subject}"))
        else:
            self.stdout.write(f"Ticket '{ticket2.subject}' already exists")

        # ── Sample Ticket 3 (Resolved) ────────────────────────────────
        ticket3, created = Ticket.objects.get_or_create(
            subject="Billing discrepancy on my last invoice",
            defaults={
                "user": user,
                "description": (
                    "I was charged $49.99 on my last invoice but my current plan should "
                    "only be $29.99 per month. I upgraded two months ago and the price "
                    "was clearly stated as $29.99.\n\n"
                    "Please find the attached invoice #INV-2024-0891 for reference."
                ),
                "priority": "high",
                "status": "resolved",
            },
        )
        t3_created_at = now - timedelta(days=7, hours=6)
        if created:
            set_ticket_time(ticket3, t3_created_at)
            self.stdout.write(self.style.SUCCESS(f"Created ticket: {ticket3.subject}"))
        else:
            self.stdout.write(f"Ticket '{ticket3.subject}' already exists")

        # ── Sample Ticket 4 (Closed) ──────────────────────────────────
        ticket4, created = Ticket.objects.get_or_create(
            subject="How to reset my password?",
            defaults={
                "user": user,
                "description": (
                    "I forgot my password and tried using the 'Forgot Password' link, "
                    "but I'm not receiving the reset email. I checked my spam folder "
                    "as well.\n\n"
                    "Can you help me reset my password manually?"
                ),
                "priority": "medium",
                "status": "closed",
            },
        )
        t4_created_at = now - timedelta(days=14, hours=2)
        if created:
            set_ticket_time(ticket4, t4_created_at)
            self.stdout.write(self.style.SUCCESS(f"Created ticket: {ticket4.subject}"))
        else:
            self.stdout.write(f"Ticket '{ticket4.subject}' already exists")

        # ── Replies for Ticket 1 (Open) ───────────────────────────────
        self._create_reply(
            staff, ticket1,
            "Hello Damodar, thank you for reaching out. Let me investigate the dashboard "
            "issue. Could you tell me which browser and operating system you're using?",
            t1_created_at + timedelta(minutes=45), set_reply_time,
        )
        self._create_reply(
            user, ticket1,
            "I'm using Chrome 124 on Windows 11. I also tried Edge and got the same error.",
            t1_created_at + timedelta(hours=2), set_reply_time,
        )
        self._create_reply(
            staff, ticket1,
            "Thanks for the details. I've escalated this to our infrastructure team. "
            "There seems to be a load-balancer issue affecting certain accounts. "
            "I'll update you as soon as we have a fix.",
            t1_created_at + timedelta(hours=3, minutes=30), set_reply_time,
        )

        # ── Replies for Ticket 2 (In Progress) ────────────────────────
        self._create_reply(
            staff, ticket2,
            "Hi Damodar, great suggestion! We've actually been working on a dark mode "
            "feature for the next release. I've added your request to the feature tracking "
            "ticket. Expected release is in the next two weeks.",
            t2_created_at + timedelta(hours=1), set_reply_time,
        )
        self._create_reply(
            user, ticket2,
            "That's great to hear! Looking forward to it. Will there be an option to "
            "toggle between light and dark modes manually?",
            t2_created_at + timedelta(days=1), set_reply_time,
        )
        self._create_reply(
            staff, ticket2,
            "Yes! The implementation includes a toggle in the settings panel, and it will "
            "also respect your system-level preference by default.",
            t2_created_at + timedelta(days=1, hours=4), set_reply_time,
        )

        # ── Replies for Ticket 3 (Resolved) ────────────────────────────
        self._create_reply(
            staff, ticket3,
            "Hello Damodar, I've checked your account and invoice. It appears there was a "
            "prorated charge from the plan change that caused the higher amount. I've "
            "issued a $20.00 credit to your account. You should see it reflected within "
            "24 hours.",
            t3_created_at + timedelta(hours=6), set_reply_time,
        )
        self._create_reply(
            user, ticket3,
            "Thank you for the quick resolution! I see the credit on my account now. "
            "Appreciate the help.",
            t3_created_at + timedelta(hours=24), set_reply_time,
        )

        # ── Replies for Ticket 4 (Closed) ─────────────────────────────
        self._create_reply(
            staff, ticket4,
            "Hi Damodar, I've manually reset your password. Your temporary password is: "
            "Temp@123456\n\n"
            "Please log in and change it immediately for security purposes. Let me know "
            "if you need any further assistance.",
            t4_created_at + timedelta(minutes=20), set_reply_time,
        )
        self._create_reply(
            user, ticket4,
            "Got it, I was able to log in and change my password. Thanks for the help!",
            t4_created_at + timedelta(hours=1), set_reply_time,
        )

        # ── Summary ────────────────────────────────────────────────────
        ticket_count = Ticket.objects.count()
        reply_count = TicketReply.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"\nDone! {ticket_count} ticket(s) and {reply_count} reply(ies) in the database."
        ))

    # ------------------------------------------------------------------
    def _create_reply(self, author, ticket, message, created_at, set_time_fn):
        reply, created = TicketReply.objects.get_or_create(
            ticket=ticket,
            author=author,
            message=message,
        )
        if created:
            set_time_fn(reply, created_at)
            self.stdout.write(f"  Reply by {author.username} on '{ticket.subject}'")
