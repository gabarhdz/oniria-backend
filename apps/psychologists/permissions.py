from rest_framework.permissions import SAFE_METHODS
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario autenticado es el propietario del objeto.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Permitir métodos de solo lectura (GET, HEAD, OPTIONS) para cualquier usuario
        if request.method in SAFE_METHODS:
            return True
        # Permitir métodos de escritura solo si el usuario autenticado es el propietario
        return obj.psychologist.user == request.user  # Verificamos directamente contra request.user


class IsFormQuestionOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para formularios y preguntas.
    Solo el propietario puede editar o eliminar.
    Todos pueden ver los formularios y preguntas.
    """
    
    def has_permission(self, request, view):
        # Permitir GET (listar formularios/preguntas) para usuarios autenticados
        if request.method in SAFE_METHODS:
            return True
        # Para POST (crear formularios/preguntas) requiere autenticación
        if request.method == 'POST':
            return request.user.is_authenticated
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para cualquier request
        if request.method in SAFE_METHODS:
            return True
        # Permisos de escritura solo para el propietario del formulario/pregunta
        return obj.psychologist == request.user  # Verificamos directamente contra request.user