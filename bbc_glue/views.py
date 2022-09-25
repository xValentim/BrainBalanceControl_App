from django.shortcuts import render, redirect
from .models import *
from bbc_glue.data_client import *

def index(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        senha = request.POST.get('senha')
        if customer_id == '595.080.896-84':
            if senha == '1':
                return redirect('home')
            elif senha == '2':
                return redirect('home_2')
        elif customer_id == '427.282.572-59':
            if senha == '1':
                return redirect('home_4')
            elif senha == '2':
                return redirect('home_6')
            return redirect('home_1')
        else:
            return redirect('index')
    else:
        return render(request, 'glue/index.html')

def home(request):
    pfm_da_valentina = PFM(customerId='595.080.896-84', customer_data=customer_data, initialInvestment=0)
    ip_da_valentina = InitPayment(pfm_da_valentina)
    credit_engine_da_valentina = CreditEngine(pfm_da_valentina)
    return render(request, 'glue/home.html', {'banks': pfm_da_valentina.allMyAccounts, 'investment': pfm_da_valentina.investment})

def home_1(request):
    pfm_da_valentina = PFM(customerId='595.080.896-84', customer_data=customer_data, initialInvestment=0)
    ip_da_valentina = InitPayment(pfm=pfm_da_valentina)
    credit_engine_da_valentina = CreditEngine(pfm=pfm_da_valentina)
    ip_da_valentina.toRealocateAccounts()
    return render(request, 'glue/bbc_1.html', {'banks': pfm_da_valentina.allMyAccounts, 'investment': pfm_da_valentina.investment})

def home_2(request):
    pfm_da_valentina = PFM(customerId='595.080.896-84', customer_data=customer_data, initialInvestment=0)
    ip_da_valentina = InitPayment(pfm_da_valentina)
    credit_engine_da_valentina = CreditEngine(pfm_da_valentina)
    ip_da_valentina.toRealocateAccounts()
    return render(request, 'glue/home_2.html', {'banks': pfm_da_valentina.allMyAccounts, 'investment': pfm_da_valentina.investment})

def home_3(request):
    pfm_da_valentina = PFM(customerId='595.080.896-84', customer_data=customer_data, initialInvestment=0)
    ip_da_valentina = InitPayment(pfm_da_valentina)
    credit_engine_da_valentina = CreditEngine(pfm_da_valentina)
    ip_da_valentina.toApplication()
    return render(request, 'glue/bcc_3.html', {'banks': pfm_da_valentina.allMyAccounts, 'investment': pfm_da_valentina.investment})

def home_4(request):
    pass