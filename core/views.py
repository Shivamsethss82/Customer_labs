from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Account, Destination
from .serializers import AccountSerializer, DestinationSerializer
import requests

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

@api_view(['GET'])
def get_destinations_by_account(request, account_id):
    try:
        account = Account.objects.get(account_id=account_id)
        destinations = account.destinations.all()
        serializer = DestinationSerializer(destinations, many=True)
        return Response(serializer.data)
    except Account.DoesNotExist:
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def incoming_data(request):
    token = request.headers.get('CL-X-TOKEN')
    if not token:
        return Response({"error": "Un Authenticate"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        account = Account.objects.get(app_secret_token=token)
    except Account.DoesNotExist:
        return Response({"error": "Un Authenticate"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        if not isinstance(request.data, dict):
            return Response({"error": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

        for destination in account.destinations.all():
            headers = destination.headers
            headers.update({'Content-Type': 'application/json'})
            if destination.http_method == 'GET':
                response = requests.get(destination.url, headers=headers, params=request.data)
            elif destination.http_method == 'POST':
                response = requests.post(destination.url, headers=headers, json=request.data)
            elif destination.http_method == 'PUT':
                response = requests.put(destination.url, headers=headers, json=request.data)
        
        return Response({"status": "Data sent successfully"})
