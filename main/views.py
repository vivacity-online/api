import random

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import FullSizeNPC, Dialogue
from main.serializers import NPCSerializer
from users.models import User


def get_NPC():
    all_NPC_characters = FullSizeNPC.objects.all()
    if all_NPC_characters.count() > 0:
        rand_int = random.randint(0, (len(all_NPC_characters) - 1))
        npc = all_NPC_characters[rand_int]
    else:
        if Dialogue.objects.all().count() < 1:
            Dialogue.objects.create(
                content="Welcome to Vivacity"
            )

        npc = FullSizeNPC.objects.create(
            image="/main/images/NPC/hunter.png",
            title="Hunter",
            alt="Hunter"
        )
        npc.dialogue.add(Dialogue.objects.all()[0])

    return npc


def get_online_users():
    users_count = User.objects.filter(online=True).count()
    return users_count


class HomeView(APIView):

    def get(self, request, *args, **kwargs):
        data = {}
        npc = get_NPC()
        serialized_npc = NPCSerializer(npc)
        data['NPC'] = serialized_npc.data
        data['online_users'] = get_online_users()
        return Response(data, status=status.HTTP_200_OK)
