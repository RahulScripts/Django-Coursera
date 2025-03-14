from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import requests, json, decimal

# Create your models here.
class Currency(models.Model):
    symbol = models.CharField(max_length=10, primary_key=True)
    usd_value = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)

    def __str__(self) -> str:
        return self.symbol
    
class Transaction(models.Model):
    origin_currency = models.ForeignKey("Currency", on_delete=models.CASCADE, related_name='origin_currency')
    destination_currency = models.ForeignKey("Currency", on_delete=models.CASCADE, related_name='destination_currency')
    original_currency_value = models.DecimalField(max_digits=10, decimal_places=2)
    desatination_currency_value = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=1.0)
    exchange_date = models.DateTimeField(auto_now_add=True)

class CurrencyHistory(models.Model):
    symbol = models.ForeignKey('Currency', on_delete=models.CASCADE)
    usd_value = models.DecimalField(max_digits=10, decimal_places=6, default=1.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.usd_value = self.get_value()
        super(CurrencyHistory, self).save(*args, **kwargs)

    def get_value(self):
        currency_code = self.symbol.symbol
        key = f"{currency_code}USD"
        api_url = f'https://economia.awesomeapi.com.br/json/last/{currency_code}-USD'
        response = requests.get(api_url)
        json_data = json.loads(response.content)
        usd_ask_value = json_data[key]['ask']
        decimal_value = decimal.Decimal(usd_ask_value)

        return decimal_value
    
class CurrencyBalance(models.Model):
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    share_portfolio= models.DecimalField(max_digits=5,decimal_places=2,default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"{self.currency.symbol} {self.value}"
    
    @property
    def usd_balance(self):
        current_usd_rate = CurrencyHistory.objects.create(symbol=self.currency)
        usd_rate = current_usd_rate.usd_value
        return usd_rate

class ExchangeGoal(models.Model):
    origin_balance = models.ForeignKey('CurrencyBalance', on_delete=models.CASCADE, related_name='exchange_goal')
    destination_currency = models.ForeignKey('Currency', on_delete=models.CASCADE, related_name='exchange_goal')
    initial_value = models.DecimalField(max_digits=10, decimal_places=2)
    threshold = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    completed =models.BooleanField(default=False)
    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE, null=True, blank=True)

    @property
    def percentage(self):
        return self.threshold*100
    
    @property
    def increase(self):
        return self.threshold*self.origin_balance.value
    
    @property
    def difference_initial_value(self):
        return self.origin_balance.value - self.initial_value
    
    @property
    def percentage_difference(self):
        return self.difference_initial_value/self.initial_value * 100