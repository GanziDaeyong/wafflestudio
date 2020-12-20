from rest_framework import serializers
from trelloclone.list.models import List
from trelloclone.card.models import Card
from trelloclone.card.serializers import BasicCardSerializer

class ListSerializer(serializers.ModelSerializer):
    cards=serializers.SerializerMethodField()
    class Meta:
        model=List
        fields=(
            'id',
            'name',
            'cards',
        )

    def get_cards(self,listobj):
        headcard=listobj.head
        firstcard=headcard.prev
        def cardlistrec(card):
            prevcard=card.prev
            returnquery=Card.objects.all().filter(id=prevcard.id)
            if prevcard:
                returnquery|=cardlistrec(prevcard)
            return returnquery
        fullquery=cardlistrec(firstcard)
        return BasicCardSerializer(fullquery,many=True)


