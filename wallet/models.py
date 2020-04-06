from django.db import models


class Wallet(models.Model):

    owner = models.CharField(max_length=50, blank=False, null=False, default="")
    shinies = models.IntegerField(
        default=0
    )
    muns = models.IntegerField(
        default=0
    )

    @property
    def balance(self):
        currencies = {
            'shinies': self.shinies,
            'muns': self.muns
        }
        return currencies

    def transact_currency(self, amount, currency):
        """Adds/Removes 'amount' of 'currency' from current wallet,
        this is the base function used in all currency
        transactions
        """
        if currency == "shinies":
            self.shinies += amount
            return self.shinies
        elif currency == 'muns':
            self.muns += amount
            return self.muns

    def send_currency(self, send_to, amount, currency):
        """Send currency to another wallet, all transactions
        are one way, no reception required.
        """
        if type(send_to) is type(self):
            # Make sure sending to another wallet object
            if not hasattr(self, currency.lower()):
                # if the 'currency' sent is not a
                # field in the wallet model
                raise AttributeError(f'No attribute {currency}')
            else:
                if type(amount) is int:
                    self.transact_currency(-amount, currency.lower())
                    send_to.transact_currency(amount, currency.lower())
                else:
                    raise TypeError(f'Must be integer, not: {type(amount)}')
        else:
            raise TypeError(f'Cannot send to type: {type(send_to)}')

    def __str__(self):
        return f'{type(self).__name__}#{self.owner.pk}'
