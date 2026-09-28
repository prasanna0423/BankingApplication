
from django.shortcuts import render, redirect
from decimal import Decimal, InvalidOperation
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Account, Transaction


def home(request):
    return render(request, 'base.html')


def register(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        phone = request.POST['phone']
        address = request.POST['address']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            password=password
        )

        Account.objects.create(
            user=user,
            account_number='ACC' + str(user.id).zfill(6),
            account_type='Savings',
            balance=Decimal('0.00'),
            phone=phone,
            address=address
        )

        messages.success(request, 'Account created successfully')

        return redirect('login')

    return render(request, 'register.html')


def login_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


def logout_view(request):

    logout(request)
    return redirect('login')


def dashboard(request):

    if not request.user.is_authenticated:
        return redirect('login')

    account = Account.objects.get(user=request.user)

    transactions = Transaction.objects.filter(
        account=account
    ).order_by('-created_at')[:5]

    return render(
        request,
        'dashboard.html',
        {
            'account': account,
            'transactions': transactions
        }
    )


def deposit(request):

    if not request.user.is_authenticated:
        return redirect('login')

    account = Account.objects.get(user=request.user)

    if request.method == 'POST':

        try:
            amount = Decimal(request.POST.get('amount', '0'))
        except (InvalidOperation, TypeError, ValueError):
            messages.error(request, 'Enter a valid amount')
            return redirect('deposit')

        if not amount.is_finite() or amount <= 0:
            messages.error(request, 'Enter a valid amount')
            return redirect('deposit')

        account.balance += amount
        account.save()

        Transaction.objects.create(
            account=account,
            transaction_type='Deposit',
            amount=amount,
            description='Money deposited'
        )

        messages.success(request, 'Amount deposited successfully')

        return redirect('dashboard')

    return render(
        request,
        'deposit.html',
        {'account': account}
    )


def withdraw(request):

    if not request.user.is_authenticated:
        return redirect('login')

    account = Account.objects.get(user=request.user)

    if request.method == 'POST':

        try:
            amount = Decimal(request.POST.get('amount', '0'))
        except (InvalidOperation, TypeError, ValueError):
            messages.error(request, 'Enter a valid amount')
            return redirect('withdraw')

        if not amount.is_finite() or amount <= 0:
            messages.error(request, 'Enter a valid amount')
            return redirect('withdraw')

        if amount > account.balance:
            messages.error(request, 'Insufficient balance')
            return redirect('withdraw')

        account.balance -= amount
        account.save()

        Transaction.objects.create(
            account=account,
            transaction_type='Withdraw',
            amount=amount,
            description='Money withdrawn'
        )

        messages.success(request, 'Amount withdrawn successfully')

        return redirect('dashboard')

    return render(
        request,
        'withdraw.html',
        {'account': account}
    )


def transfer(request):

    if not request.user.is_authenticated:
        return redirect('login')

    sender = Account.objects.get(user=request.user)

    if request.method == 'POST':

        receiver_number = request.POST.get(
            'account_number',
            ''
        ).strip().upper()

        try:
            amount = Decimal(
                request.POST.get('amount', '0')
            )
        except (InvalidOperation, TypeError, ValueError):

            messages.error(
                request,
                'Enter a valid amount'
            )

            return redirect('transfer')

        if not amount.is_finite() or amount <= 0:

            messages.error(
                request,
                'Enter a valid amount'
            )

            return redirect('transfer')

        try:

            receiver = Account.objects.get(
                account_number=receiver_number
            )

        except Account.DoesNotExist:

            messages.error(
                request,
                'Receiver account not found'
            )

            return redirect('transfer')

        if receiver.pk == sender.pk:

            messages.error(
                request,
                'You cannot transfer to your own account'
            )

            return redirect('transfer')

        if amount > sender.balance:

            messages.error(
                request,
                'Insufficient balance'
            )

            return redirect('transfer')

        # Remove money from sender
        sender.balance -= amount

        # Add money to receiver
        receiver.balance += amount

        sender.save()
        receiver.save()

        # Sender transaction
        Transaction.objects.create(
            account=sender,
            transaction_type='Transfer',
            amount=amount,
            description=f'Transferred to {receiver.account_number}'
        )

        # Receiver transaction
        Transaction.objects.create(
            account=receiver,
            transaction_type='Transfer',
            amount=amount,
            description=f'Received from {sender.account_number}'
        )

        messages.success(
            request,
            'Money transferred successfully'
        )

        return redirect('dashboard')

    return render(
        request,
        'transfer.html',
        {
            'account': sender
        }
    )



def transactions(request):

    if not request.user.is_authenticated:
        return redirect('login')

    account = Account.objects.get(user=request.user)

    transaction_list = Transaction.objects.filter(
        account=account
    ).order_by('-created_at')

    return render(
        request,
        'transactions.html',
        {
            'account': account,
            'transactions': transaction_list
        }
    )