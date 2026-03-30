from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Claim
from .services.s3_service import upload_to_s3

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_claim(request):
    file = request.FILES.get('image')

    if not file:
        return Response({"error": "No file uploaded"})

    file_name = file.name

    
    image_url = upload_to_s3(file, file_name)

    
    claim = Claim.objects.create(
        user=request.user,
        image_url=image_url,
        status="uploaded"
    )

    return Response({
        "msg": "Uploaded successfully",
        "image_url": image_url,
        "claim_id": claim.id
    })



from django.http import HttpResponse


def home(request):
    return HttpResponse("ClaimGuard")

