from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from services.aiImplementation.deepseek_basic_call import deepseek_basic_call
# Create your views here.

class AI_basic_call(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        prompt = data.get("prompt")

        deepseek = deepseek_basic_call()
        result = deepseek(prompt)

        return Response({"result": result})

