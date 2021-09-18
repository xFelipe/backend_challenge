import logging
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from car.models import Car, Tyre
from math import gcd

logging.getLogger().setLevel(logging.INFO)

# Create your tests here.
class ChallengeTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        logging.info(self.client.post('/CreateCar').json())
        logging.info(
            self.client.post('/Refuel', data={"car": 1, "gas_quantity": 54}).json()
        )
        for _ in range(4):
            logging.info(
                self.client.post('/CreateTyre', data={'car': 1}).json()
            )

    def test_ok(self):
        challenge_km = 10000
        km_to_finish_gas = Car.KILOMETERS_PER_LITRE * Car.MAX_GAS_LITRES
        km_to_tyre_degradation = km_to_finish_gas/3
        maximum_common_divisor = gcd(
            int(km_to_finish_gas), int(km_to_tyre_degradation), int(challenge_km)
        )
        for i in range(1, int(challenge_km/maximum_common_divisor)+1):
            logging.info(f'Running to {i*maximum_common_divisor} km')
            run_request = self.client.post('/Trip', data={"car": 1,"distance": 5})
            self.assertEquals(200, run_request.status_code)

            if i*maximum_common_divisor % km_to_tyre_degradation == 0:
                for _ in range(4):
                    self.client.post('/CreateTyre', data={'car': 1}).json()
            if i*maximum_common_divisor % km_to_finish_gas == 0:
                self.client.post('/Refuel', data={"car": 1, "gas_quantity": 54})