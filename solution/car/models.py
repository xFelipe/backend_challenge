from decimal import Decimal
from fractions import Fraction
from django.db import models


# Create your models here.
class Car(models.Model):
    KILOMETERS_PER_LITRE = 8
    gas_level = models.DecimalField(max_digits=9, decimal_places=6)

    def run(self, kms: Decimal):
        if not self.pk:
            raise ReferenceError("Unsaved car can't run.")

        new_gas_level = self.gas_level - (kms / self.KILOMETERS_PER_LITRE)
        if new_gas_level < 0:
            raise ValueError(
                f'Impossible to run {kms} km '
                f'with {self.gas_level} liters of gas.'
            )
        car_tyres = Tyre.objects.filter(car__pk=self.pk)
        if not all(tyre.may_run(kms) for tyre in car_tyres):
            raise ValueError(f'Car tyres can\'t handle run {kms} km.')

        for tyre in car_tyres:
            tyre.run(kms)
            tyre.save()
        self.gas_level = new_gas_level
        self.save()


class Tyre(models.Model):
    DEGRADATION_PER_KILOMETER = Fraction(1, 3)
    km_traveled = models.DecimalField(max_digits=5, decimal_places=2)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    def may_run(self, kms: Decimal) -> bool:
        return (self.km_traveled + kms) * self.DEGRADATION_PER_KILOMETER <= 100

    def run(self, kms: Decimal) -> Decimal:
        if not self.may_run(kms):
            raise ValueError(f'Tyres can\'t handle run {kms} km.')
        self.km_traveled += kms
        self.save()