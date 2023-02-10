from django.db import models
from django.contrib.auth.models import User
from djongo.models.fields import ObjectIdField, EmbeddedField
from datetime import datetime

ORDER_TYPES = [('BUY', 'buy'), ('SELL', 'sell')]

class Wallet(models.Model):
    
    btc_balance = models.FloatField()
    starting_btc_balance = models.FloatField(default=False)
    usd_balance = models.FloatField()

    class Meta:
        abstract = True


class Profile(models.Model):

    _id = ObjectIdField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet = EmbeddedField(
        model_container=Wallet
    )

    def __str__(self):
        return self.user.username


class Order(models.Model):
    
    _id = ObjectIdField()
    user = models.CharField(max_length=20, unique=False)
    type = models.CharField(max_length=10, choices=ORDER_TYPES)
    amount = models.FloatField()
    price = models.FloatField()
    date_created = models.DateTimeField(default=datetime.now )
    filled = models.BooleanField(default=False)
    quote_filled = models.FloatField(default=0)
    date_filled = models.DateTimeField(default=None)

    def __str__(self):
        return str(self.pk)





