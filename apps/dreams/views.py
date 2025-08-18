from django.shortcuts import render
from services.aiImplementation.deepseek_basic_call import deepseek_basic_call
# Create your views here.
class AI_basic_call:
    def post(self,request,*args,**kwargs):
        data = request.data
        user = request.user
        response = deepseek_basic_call(data.prompt)
        return(response)