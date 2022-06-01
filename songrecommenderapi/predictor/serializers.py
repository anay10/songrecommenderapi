from rest_framework import serializers

class PredictUserEmotionSerializer(serializers.Serializer):
    xinput = serializers.CharField(max_length = 50, min_length = 10)

    class Meta:
        fields = ['xinput',]

    def validate(self, attrs):
        try:
            Xvariable = attrs.get('xinput')
        except Exception as e:
            raise AttributeError('Invalid atrributes')

        return super().validate(attrs)