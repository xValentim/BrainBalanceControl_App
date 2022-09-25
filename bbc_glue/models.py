from django.db import models
import requests
import time
from bbc_glue.data_client import *
from datetime import datetime

'''
Aqui vamos criar uma classe que representará uma aplicação 
de alta liquidez e baixo risco.
'''

class AccountId(models.Model):
    AccountId = models.CharField(max_length=200)

    def __str__(self) -> str:
        return str(self.id) + ' - ' + self.AccountId


class Account(models.Model):
    def __init__(self, accountId, balance, customerId, organizationId, creditCards, bill) -> None:
        self.accountId = accountId
        self.balance = balance
        self.customerId = customerId
        self.name = accountId[:4]
        self.organizationId = organizationId
        self.creditCards = creditCards
        self.bill = round(bill, 2)
        self.log = 'Detalhes das contas do cliente ' + self.customerId + '\n' + '----------------------------------------\n'

    def showAllSituation(self) -> str:
        return f"Conta: {self.accountId} | Saldo: {self.balance} | Cliente: {self.customerId} | Organização: {self.organizationId} | Cartões de crédito: {self.creditCards} | Fatura: {self.bill}\n"
        
    def getAccountId(self) -> str:
        return self.accountId
    
    def getBalance(self) -> float:
        return self.balance
    
    def getCustomerId(self) -> str:
        return self.customerId
    
    def getOrganizationId(self) -> str:
        return self.organizationId
    
    def toWithdraw(self, amount: float) -> float:
        self.log(f"Saque de {amount} na conta {self.accountId} em {datetime.now()}\n")
        self.balance -= amount
        return amount
    
    def toDeposit(self, amount: float) -> None:
        self.log += f"Depósito de {amount} na conta {self.accountId} em {datetime.now()}\n"
        self.balance += amount
    
    def toTransfer(self, amount: float, account, isToMe: bool = True) -> None:
        if isToMe:
            self.log += f"Transferência de {amount} da conta {self.accountId} para a conta {account.getAccountId()} em {datetime.now()} (Remanejamento entre suas contas)\n"
            self.balance -= amount
            account.balance += amount
        else:
            self.log += f"Transferência de {amount} da conta {self.accountId} para a conta {account.getAccountId()} em {datetime.now()} (Remanejamento entre contas de terceiros)\n"
            self.balance -= amount
            account.balance += amount
    
    def toInvestment(self, amount: float, investment) -> None:
        self.balance -= amount
        investment.investmentValue += amount
        self.log += f"Investimento de {amount} na conta de investimentos 0001 em {datetime.now()} (Liquidez: {investment.getLiquidity()} || Risco: {investment.getRisk()})\n"
        print(f"Investimento de {amount} na conta de investimentos 0001 em {datetime.now()} (Liquidez: {investment.getLiquidity()} || Risco: {investment.getRisk()})\n")

class Investment(models.Model):
    def __init__(self, investmentValue, liquidity="high", risk="low") -> None:
        self.investmentValue = investmentValue
        self.liquidity = liquidity
        self.risk = risk

    def getInvestmentValue(self) -> float:
        return self.investmentValue
    
    def getLiquidity(self) -> str:
        return self.liquidity
    
    def getRisk(self) -> str:
        return self.risk
    
    # Aplicação em investimentos de alta liquidez e baixo risco default 0 
    def toWithdrawInvestment(self, amount: float=-1) -> float:
        if amount == -1:
            amount = self.investmentValue
            self.investmentValue = 0
            return amount
        else:
            self.investmentValue -= amount
            return amount
        
    # def toApplication(self, amount: float) -> None:
    #     self.investmentValue += amount

class PFM(models.Model):
    def __init__(self, customerId: str, customer_data: dict, initialInvestment: float=0) -> None:
        self.customerId = customerId
        self.listAccountIds = customer_data['listAccountIds']
        self.listOrgsIds = customer_data['listOrgsIds']
        self.params = [self.customerId] + customer_data['params']
        self.listCreditCardAccountId = self.getListCreditCardAccountId()
        self.investment = Investment(initialInvestment)
        self.allAccounts = self.getAllAccounts()
        self.log = ''

        self.myBill = self.getMyBill()
        # self.totalBalance = self.getTotalBalance()
        # self.accountNegative = self.getAccountNegative()
        # self.accountPositive = self.getAccountPositive()
        # self.allAmounts = self.getAllAmounts()
        self.salaries = self.getSalary()
        self.totalSalary = sum(self.salaries)
        # self.totalAmounts = sum(self.allAmounts)
        self.totalBill = sum(self.myBill)
        self.totalInvestment = self.investment.getInvestmentValue()
        # self.total = self.totalBalance + self.totalInvestment
        self.allMyAccounts = [Account(account[2], account[3], self.customerId, account[1], self.listCreditCardAccountId[index], self.myBill[index]) for index, account in enumerate(self.allAccounts)]

    def getAllDebt(self) -> list:
        valueAccount = sum([account.getBalance() for account in self.allMyAccounts])
        valueBill = self.totalBill
        valueInvestment = self.totalInvestment
        total = valueAccount + valueBill + valueInvestment
        if total < 0:
            return total
        return 0

    def showAllMySituation(self) -> None:
        log = ''
        for account in self.allMyAccounts:
            log += account.showAllSituation()
        log += f"Total de investimentos: {self.investment.investmentValue}\n"
        return log

    def getMyAccountsNegative(self) -> list:
        accs = [account for account in self.allMyAccounts if account.getBalance() < 0]
        accs = sorted(accs, key=lambda x: x.getBalance())
        return accs
    
    def getMyAccountsPositive(self) -> list:
        accs = [account for account in self.allMyAccounts if account.getBalance() >= 0]
        accs = sorted(accs, key=lambda x: x.getBalance(), reverse=True)
        return accs
    
    def myTotalBalance(self) -> float:
        return sum([account.getBalance() for account in self.allMyAccounts])
    
    def canIRealocate(self) -> bool:
        return self.myTotalBalance() > 0

    # Todos os métodos que consultam as APIS para obter os dados do cliente
    def getAllAmounts(self) -> float:
        # Get amount of account_id
        allAmounts = []
        for i in range(len(self.listAccountIds)):
            orgId = self.listOrgsIds[i]
            accountId = self.listAccountIds[i]
            customerId = self.params[i]
            headers = {'organizationid': orgId, 'customerid': customerId}
            link = f'https://challenge.hackathonbtg.com/accounts/v1/accounts/{accountId}/balances'
            response = requests.get(url=link, headers=headers).json()
            time.sleep(0.02)
            allAmounts.append(response['data']['availableAmount'])
        return allAmounts

    def getAccountNegative(self) -> list:
        # Get account_id negative
        accountNegative = []
        for i in range(len(self.listAccountIds)):
            orgId = self.listOrgsIds[i]
            accountId = self.listAccountIds[i]
            customerId = self.params[i]
            headers = {'organizationid': orgId, 'customerid': customerId}
            link = f'https://challenge.hackathonbtg.com/accounts/v1/accounts/{accountId}/balances'
            response = requests.get(url=link, headers=headers).json()
            time.sleep(0.02)
            if response['data']['availableAmount'] < 0:
                accountNegative.append([i, orgId, accountId])
        return accountNegative
    
    def getAccountPositive(self) -> list:
        # Get account_id positive
        accountPositive = []
        for i in range(len(self.listAccountIds)):
            orgId = self.listOrgsIds[i]
            accountId = self.listAccountIds[i]
            customerId = self.params[i]
            headers = {'organizationid': orgId, 'customerid': customerId}
            link = f'https://challenge.hackathonbtg.com/accounts/v1/accounts/{accountId}/balances'
            response = requests.get(url=link, headers=headers).json()
            time.sleep(0.02)
            if response['data']['availableAmount'] > 0:
                accountPositive.append([i, orgId, accountId])
        return accountPositive
    
    def getAllAccounts(self) -> list:
        # Get all accounts
        allAccounts = []
        for i in range(len(self.listAccountIds)):
            orgId = self.listOrgsIds[i]
            accountId = self.listAccountIds[i]
            customerId = self.params[i]
            headers = {'organizationid': orgId, 'customerid': customerId}
            link = f'https://challenge.hackathonbtg.com/accounts/v1/accounts/{accountId}/balances'
            response = requests.get(url=link, headers=headers).json()
            time.sleep(0.02)
            allAccounts.append([i, orgId, accountId, response['data']['availableAmount']])
        return allAccounts

    def getSalary(self) -> float:
        # Get salary
        salaries = []
        for i in range(len(self.listAccountIds)):
            orgId = self.listOrgsIds[i]
            accountId = self.listAccountIds[i]
            customerId = self.params[i]
            headers = {'organizationid': orgId, 'customerid': customerId}
            link = 'https://challenge.hackathonbtg.com/customers/v1/personal/qualifications'
            response = requests.get(url=link, headers=headers).json()
            salaries.append(response['data']['informedIncome']['amount'])
            time.sleep(0.02)
        return salaries

    def getListCreditCardAccountId(self) -> list:
        creditCardAccountId = []
        for i in range(len(self.listAccountIds)):
            orgId = self.listOrgsIds[i]
            accountId = self.listAccountIds[i]
            customerId = self.params[i]
            headers = {'organizationid': orgId, 'customerid': customerId}
            link = f'https://challenge.hackathonbtg.com/credit-cards-accounts/v1/accounts'
            response = requests.get(url=link, headers=headers).json()
            time.sleep(0.02)
            creditCardAccountId.append(response['data'][0]['creditCardAccountId'])
        return creditCardAccountId
    
    def getMyBill(self) -> float:
        mybills= []
        for i in range(len(self.listAccountIds)):
            orgId = self.listOrgsIds[i]
            accountId = self.listAccountIds[i]
            customerId = self.params[i]
            creditCardAccountId = self.listCreditCardAccountId[i]
            headers = {'organizationid': orgId, 'customerid': customerId}
            link = f'https://challenge.hackathonbtg.com/credit-cards-accounts/v1/accounts/{creditCardAccountId}/bills'
            response = requests.get(url=link, headers=headers).json()
            time.sleep(0.02)
            mybills.append(response['data'][0]['billTotalAmount'])
        return mybills
    
    def getTotalBalance(self):
        return  sum(self.getAllAmounts()) + sum(self.getSalary()) - sum(self.getMyBill())
        

class CreditEngine(models.Model):
    def __init__(self, pfm: PFM) -> None:
        self.pfm = pfm
        self.i = 0.02
        self.risk = 0
        self.riskThreshold = 3
        self.refreshRisk()
    
    def coefficient(self, n: int) -> float:
        return (((1 + self.i) ** n)* self.i) / (((1 + self.i) ** n) - 1)
    
    def refreshRisk(self) -> None:
        if self.pfm.getAllDebt() < 0 and self.pfm.totalBill > 0.3 * self.pfm.totalSalary:
            self.risk += 1
        if (self.pfm.getAllDebt() < 0 and self.pfm.totalBill >= self.pfm.totalSalary) or self.pfm.totalBill >= self.pfm.totalSalary:
            self.risk += 3
    
    def isRisk(self) -> bool:
        return self.risk >= self.riskThreshold
    
    def creditProposal(self, valueZero, n):
        parcela = valueZero * self.coefficient(n)
        return parcela
    
    # Simple Policy
    def offer(self) -> str:
        pass

class InitPayment(models.Model):
    def __init__(self, pfm: PFM) -> None:
        self.pfm = pfm
        self.log = ''
    
    # Remanejamento entre contas
    def toRealocateAccounts(self):
        if len(self.pfm.getMyAccountsNegative()) > 0 and self.pfm.canIRealocate():
            myAccountsNegative = self.pfm.getMyAccountsNegative()
            myAccountsPositive = self.pfm.getMyAccountsPositive()
            for i in range(len(myAccountsPositive)):
                for j in range(len(myAccountsNegative)):
                    myAccountsPositive[i].toTransfer(min(myAccountsPositive[i].getBalance(), abs(myAccountsNegative[j].getBalance())), myAccountsNegative[j], isToMe=True)
                    if myAccountsNegative[j].getBalance() == 0:
                        break
                if myAccountsPositive[i].getBalance() == 0:
                    break
            self.log += 'Remanejamento entre contas concluído\n'
        elif len(self.pfm.getMyAccountsNegative()) > 0 and not self.pfm.canIRealocate():
            self.log += 'Não foi possível realizar o remanejamento entre contas. Seu saldo total é negativo\n'
        else:
            self.log += 'Não foi necessário realizar o remanejamento entre contas\n'

    # Aplicação em investimentos de alta liquidez e baixo risco
    def toApplication(self):
        if len(self.pfm.getMyAccountsNegative()) > 0 and self.pfm.canIRealocate():
            self.toRealocateAccounts()
        if self.pfm.myTotalBalance() > 0:
            myAccountsPositive = self.pfm.getMyAccountsPositive()
            for i in range(len(myAccountsPositive)):
                myAccountsPositive[i].toInvestment(myAccountsPositive[i].getBalance(), self.pfm.investment)
                self.log += 'Aplicação em investimentos de alta liquidez e baixo risco concluída\n'
        

    # Negativado, não vai conseguir pagar as faturas, portanto, acionaremos o motor de crédito
    def toCredit(self, creditEngine: CreditEngine, n: int) -> None:
        if creditEngine.isRisk():
            valueZero = abs(self.pfm.getAllDebt())
            parcela = creditEngine.creditProposal(valueZero, n)
            self.log += 'Negativado, não vai conseguir pagar as faturas, portanto, acionaremos o motor de crédito\n'
            self.log += f'O motor de crédito irá fornecer uma oferta de crédito de {n} parcelas de {parcela} para pagar a dívida de {valueZero}\n'
            # To zero all balance and all bills of all my accounts
            myAccountsNeg = self.pfm.getMyAccountsNegative()
            for i in range(len(myAccountsNeg)):
                myAccountsNeg[i].balance = 0
                myAccountsNeg[i].bill = 0
            self.log += 'Todas as contas foram zeradas\n'
            self.log += 'Adiciona primeira fatura do acordo\n'
            self.pfm.allMyAccounts[0].bill = parcela
        else:
            self.log += 'Não foi necessário acionar o motor de crédito\n'
        

    # Retira valor investido para pagar as faturas
    def toWithdrawInvestmentToPayBank(self):
        myNegativeAccounts = self.pfm.getMyAccountsNegative()
        myNegativeBalance = sum([account.getBalance() for account in myNegativeAccounts])
        investValue = self.pfm.investment.investmentValue
        if len(myNegativeAccounts) > 0 and not self.pfm.canIRealocate() and investValue > abs(myNegativeBalance):
            self.pfm.investment.toWithdrawInvestment(abs(myNegativeBalance))
            for i in range(len(myNegativeAccounts)):
                myNegativeAccounts[i].balance = 0
            self.log += f'Retirada de valor investido de {abs(myNegativeBalance)} para pagar dívidas concluída\n'
        else:
            self.log += 'Não foi necessário retirar valor investido para pagar dívidas\n'
        

    def toPayment(self, amount: float, typePayment: str = 'me2me') -> None:
        link = 'https://api-h.developer.btgpactual.com/tr/payment-initiation/payment/pix'
        # Get account_id negative
        if typePayment == 'me2me':
            pass
        elif typePayment == 'me2other':
            pass





