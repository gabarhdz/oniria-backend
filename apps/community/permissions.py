from rest_framework.permissions import SAFE_METHODS
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author.id == request.user.id  # Para posts


class IsCommunityOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para comunidades.
    Solo el propietario puede editar o eliminar la comunidad.
    Todos pueden ver las comunidades.
    """
    
    def has_permission(self, request, view):
        # Permitir GET (listar comunidades) para usuarios autenticados
        if request.method in SAFE_METHODS:
            return True
        # Para POST (crear comunidad) requiere autenticación
        if request.method == 'POST':
            return request.user.is_authenticated
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para cualquier request
        if request.method in SAFE_METHODS:
            return True
        
        # Permisos de escritura solo para el propietario de la comunidad
        return obj.owner == request.user