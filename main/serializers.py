from rest_framework import serializers

from main.models import FullSizeNPC, Dialogue


class DialogueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dialogue
        fields = '__all__'


class NPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = FullSizeNPC
        fields = '__all__'

    dialogue = DialogueSerializer(many=True)
