from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from services.aiImplementation.deepseek_basic_call import deepseek_basic_call
import logging

logger = logging.getLogger(__name__)

class ChatAPIView(APIView):
    """
    Endpoint para chat con DeepSeek AI
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Recibe un mensaje del usuario y devuelve la respuesta de DeepSeek
        """
        try:
            # Obtener el mensaje del request
            message = request.data.get('message', '').strip()
            
            if not message:
                return Response(
                    {'error': 'El mensaje no puede estar vacío'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Usuario {request.user.username} envió mensaje: {message[:50]}...")
            
            # Llamar a DeepSeek
            deepseek = deepseek_basic_call()
            ai_response = deepseek(message)
            
            logger.info(f"Respuesta de DeepSeek recibida exitosamente")
            
            return Response({
                'message': ai_response,
                'user': request.user.username
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en ChatAPIView: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error al procesar el mensaje: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )