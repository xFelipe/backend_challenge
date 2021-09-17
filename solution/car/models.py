from decimal import Decimal
from fractions import Fraction
from django.db import models, transaction
from django.shortcuts import get_object_or_404


# Create your models here.
class Car(models.Model):
    KILOMETERS_PER_LITRE = 8
    MAX_GAS_LITRES = 54

    gas_level = models.DecimalField(max_digits=9, decimal_places=6, default=0)

    @property
    def resume(self):
        tyres = [tyre.resume for tyre in Tyre.objects.filter(car__pk=self.pk)]
        return {
            'id': self.pk,
            'gas_level': f'{self.gas_percent:.2f}%',
            'tyres': tyres,
        }

    @property
    def gas_percent(self):
        return (self.gas_level / self.MAX_GAS_LITRES) * 100

    def run(self, kms: Decimal):
        if not self.pk:
            raise ReferenceError("Unsaved car can't run.")
        if len(Tyre.objects.filter(car=self)) != 4:
            raise ValueError("Impossible to run without 4 tyres.")

        new_gas_level = float(self.gas_level) - float(kms / self.KILOMETERS_PER_LITRE)
        if new_gas_level < 0:
            raise ValueError(
                f'Impossible to run {kms} km '
                f'with {self.gas_level:.2f} liters of gas.'
            )
        car_tyres = Tyre.objects.filter(car__pk=self.pk)
        if not all(tyre.may_run(kms) for tyre in car_tyres):
            raise ValueError(f'Car tyres can\'t handle run {kms} km.')

        for tyre in car_tyres:
            tyre.run(kms)
            tyre.save()
        self.gas_level = new_gas_level
        self.save()

    def refuel(self, gas_quantity):
        new_gas_quantity = float(self.gas_level) + gas_quantity
        if gas_quantity < 0:
            raise ValueError('Impossible refuel a negative quantity of gas.')
        if self.gas_percent >= 5:
            raise ValueError('Impossible refuel while gas level not is lower than 5%.')
        if new_gas_quantity > self.MAX_GAS_LITRES:
            new_gas_quantity = self.MAX_GAS_LITRES
        self.gas_level = new_gas_quantity
        self.save()

    def swap_tyre(self, tyre_id: int):
        old_tyre = get_object_or_404(Tyre, pk=tyre_id, car__pk=self.pk)
        if old_tyre.degradation <= 94:
            raise ValueError(
                "Can't swap a tyre with less than 94% of degradation. "
                f"(actual: {old_tyre.degradation:.2f}%)"
            )
        with transaction.atomic():
            old_tyre.delete()
            new_tyre = Tyre(car=self)
            new_tyre.save()
        return new_tyre
    
    def add_tyre(self):
        car_tyres = Tyre.objects.filter(car=self)
        if len(car_tyres) >= 4:
            most_degradated_tyre = sorted(car_tyres,
                                          key=lambda t: t.degradation,
                                          reverse=True)[0]
            if most_degradated_tyre.degradation >= 95:
                return self.swap_tyre(most_degradated_tyre.pk)
            raise ValueError("Unable to add tyre on a car that has no less than 4 good tyres.")
        new_tyre = Tyre(car=self)
        new_tyre.save()
        return new_tyre

class Tyre(models.Model):
    DEGRADATION_PER_KILOMETER = Fraction(1, 3)

    km_traveled = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    @property
    def degradation(self):
        return float(self.km_traveled) * self.DEGRADATION_PER_KILOMETER

    @property
    def resume(self):
        return {'id': self.pk, 'degradation': f'{self.degradation:.2f}%'}

    def may_run(self, kms: float) -> bool:
        return (float(self.km_traveled) + kms) * self.DEGRADATION_PER_KILOMETER <= 100

    def run(self, kms: Decimal) -> Decimal:
        if not self.may_run(kms):
            raise ValueError(f'Tyres can\'t handle run {kms} km.')
        self.km_traveled = float(self.km_traveled) + kms
        self.save()
