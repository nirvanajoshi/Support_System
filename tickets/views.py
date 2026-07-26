from django.shortcuts import render, redirect, get_object_or_404
from .models import Ticket, TicketReply
from .forms import TicketForm, TicketReplyForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('ticket_list')
    else:
        form = UserCreationForm()
    return render(request, 'tickets/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('ticket_list')
    else:
        form = AuthenticationForm()
    return render(request, 'tickets/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('ticket_list')


@login_required
def ticket_list(request):
    if request.user.is_staff:
        tickets = Ticket.objects.all().order_by('-created_at')
    else:
        tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})


@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, 'Ticket created successfully.')
            return redirect('ticket_list')
    else:
        form = TicketForm()
    return render(request, 'tickets/create_ticket.html', {'form': form})


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if not request.user.is_staff and ticket.user != request.user:
        messages.error(request, "You don't have permission to view this ticket.")
        return redirect('ticket_list')

    replies = ticket.ticketreply_set.all().order_by('created_at')

    if request.method == 'POST':
        form = TicketReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.ticket = ticket
            reply.author = request.user
            reply.save()
            messages.success(request, 'Reply posted.')
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketReplyForm()

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'replies': replies,
        'form': form,
    })


@login_required
def update_status(request, ticket_id):
    if not request.user.is_staff:
        messages.error(request, "Only staff can update ticket status.")
        return redirect('ticket_list')
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        ticket.status = new_status
        ticket.save()
        messages.success(request, 'Status updated.')
    return redirect('ticket_detail', ticket_id=ticket.id)