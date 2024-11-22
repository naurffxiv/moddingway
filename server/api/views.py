from rest_framework.decorators import api_view

from rest_framework.response import Response
from rest_framework import status
from .models import User, Exile, Strike
from .serializer import UserSerializer
import datetime


@api_view(["GET"])
def get_user(request):
    return Response(
        UserSerializer(
            {
                "userid": 231,
                "discorduserid": "discordidhere",
                "discordguildid": "guildidhere",
                "ismod": False,
                "temporarypoints": 0,
                "permanentpoints": 0,
                "createtimestamp": datetime.datetime.now(),
            }
        ).data
    )
