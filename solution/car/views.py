import logging
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from car.models import Car, Tyre

logging.getLogger().setLevel(logging.INFO)


# Create your views here.
@api_view(['POST'])
def create_car(request):
    """Create a car and return its full status"""
    car = Car()
    car.save()
    return Response(
        car.resume,
        status=201
    )

@api_view()
def get_car_status(request):
    try:
        car_pk = int(request.data['car'])
    except (ValueError, KeyError) as e:
        logging.exception(e)
        return Response({
            'error': 'Missing required field(s) in request json.',
            'required_fields': ['car: {car_id}']
        }, status=400)
    car = get_object_or_404(Car, pk=car_pk)
    return Response({'message': car.resume})

@api_view(['POST'])
def trip(request):
    try:
        car_pk = int(request.data['car'])
        distance = float(request.data['distance'])
    except (ValueError, KeyError) as e:
        logging.exception(e)
        return Response(
            {
                'error': 'Missing required field(s) in request json.',
                'fields': ['car: {int car_id}', 'distance: {float distance}']
            },
            400
        )
    car = get_object_or_404(Car, pk=car_pk)
    try:
        car.run(distance)
    except Exception as e:
        return _error(e)
    return Response({'car': car.resume})

@api_view(['POST'])
def refuel(request):
    try:
        car_pk = int(request.data['car'])
        gas_quantity = float(request.data['gas_quantity'])
    except (ValueError, KeyError) as e:
        logging.exception(e)
        return Response(
            {
                'error': 'Missing required field(s) in request json.',
                'fields': ['car: {int car_id}', 'gas_quantity: {float gas_quantity}']
            },
            400
        )
    car = get_object_or_404(Car, pk=car_pk)
    try:
        car.refuel(gas_quantity)
    except ValueError as e:
        return _error(e)
    return Response({'gas_count': f'{car.gas_percent:.2f}%'})

@api_view(['POST'])
def maintenance(request):
    try:
        car_pk = int(request.data['car'])
        tyre_pk = int(request.data['part_to_replace'])  # Acepted: 'tyres'
    except (ValueError, KeyError) as e:
        logging.exception(e)
        return Response(
            {
                'error': 'Missing required field(s) in request json.',
                'fields': ['car: {int car_id}', 'part_to_replace: {int tyre_id}']
            },
            400
        )
    car = get_object_or_404(Car, pk=car_pk)
    try:
        car.swap_tyre(tyre_pk)
    except ValueError as e:
        return _error(e)
    return Response({'car': car.resume})

@api_view(['POST'])
def create_tyre(request):
    try:
        car_pk = int(request.data['car'])
    except (ValueError, KeyError) as e:
        logging.exception(e)
        return Response({
            'error': 'Missing required field(s) in request json.',
            'required_fields': ['car: {car_id}']
        }, status=400)
    car = get_object_or_404(Car, pk=car_pk)
    try:
        car.add_tyre()
    except ValueError as e:
        return _error(e)
    return Response(car.resume)


def _error(e: Exception):
    logging.exception(e)
    return Response({'detail': str(e)}, status=400)
