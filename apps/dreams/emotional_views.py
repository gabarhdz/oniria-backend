from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from collections import Counter

from .models import EmotionalEntry, EmotionalCategory, EmotionalMilestone, emotions
from .serializers import (
    EmotionalEntrySerializer,
    EmotionalCategorySerializer,
    EmotionalMilestoneSerializer,
    EmotionalStatsSerializer,
    EmotionSerializer
)
from services.aiImplementation.deepseek_basic_call import deepseek_basic_call


class EmotionalCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar categorías emocionales
    """
    permission_classes = [IsAuthenticated]
    queryset = EmotionalCategory.objects.all()
    serializer_class = EmotionalCategorySerializer


class EmotionalEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar entradas del diario emocional
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmotionalEntrySerializer
    
    def get_queryset(self):
        """Filtrar entradas por usuario autenticado"""
        queryset = EmotionalEntry.objects.filter(user=self.request.user)
        
        # Filtros opcionales
        mood = self.request.query_params.get('mood', None)
        if mood:
            queryset = queryset.filter(mood=mood)
        
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(categories__id=category)
        
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(entry_date__range=[start_date, end_date])
        
        is_favorite = self.request.query_params.get('is_favorite', None)
        if is_favorite == 'true':
            queryset = queryset.filter(is_favorite=True)
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search) | Q(tags__icontains=search)
            )
        
        return queryset.select_related('user').prefetch_related('categories', 'emotions')
    
    def perform_create(self, serializer):
        """Asignar usuario al crear entrada"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def analyze_with_ai(self, request, pk=None):
        """
        Analizar entrada con IA (DeepSeek)
        """
        entry = self.get_object()
        
        try:
            # Construir prompt para análisis
            prompt = f"""
            Analiza la siguiente entrada de diario emocional y proporciona:
            1. Un resumen empático de la situación
            2. Identificación de emociones principales
            3. Patrones emocionales detectados
            4. Sugerencias constructivas para el bienestar emocional
            5. Ejercicios o técnicas recomendadas
            
            Título: {entry.title}
            Contenido: {entry.content}
            Estado de ánimo: {entry.get_mood_display()}
            Intensidad: {entry.intensity}/10
            """
            
            # Llamar a DeepSeek
            deepseek = deepseek_basic_call()
            analysis = deepseek(prompt)
            
            # Guardar análisis
            entry.ai_analysis = analysis
            entry.ai_analyzed_at = timezone.now()
            entry.save()
            
            serializer = self.get_serializer(entry)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error al analizar: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['patch'])
    def toggle_favorite(self, request, pk=None):
        """Marcar/desmarcar como favorito"""
        entry = self.get_object()
        entry.is_favorite = not entry.is_favorite
        entry.save()
        
        serializer = self.get_serializer(entry)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Obtener estadísticas del diario emocional
        """
        entries = self.get_queryset()
        
        # Fechas de referencia
        now = timezone.now()
        start_of_week = now - timedelta(days=now.weekday())
        start_of_month = now.replace(day=1)
        
        # Total de entradas
        total_entries = entries.count()
        
        # Entradas este mes y semana
        entries_this_month = entries.filter(entry_date__gte=start_of_month.date()).count()
        entries_this_week = entries.filter(entry_date__gte=start_of_week.date()).count()
        
        # Distribución de estados de ánimo
        mood_counts = entries.values('mood').annotate(count=Count('id'))
        mood_distribution = {item['mood']: item['count'] for item in mood_counts}
        
        # Intensidad promedio
        avg_intensity = entries.aggregate(avg=Avg('intensity'))['avg'] or 0
        
        # Emociones más comunes
        emotion_counts = Counter()
        for entry in entries.prefetch_related('emotions'):
            for emotion in entry.emotions.all():
                emotion_counts[emotion.name] += 1
        most_common_emotions = [
            {'name': name, 'count': count}
            for name, count in emotion_counts.most_common(5)
        ]
        
        # Categorías más comunes
        category_counts = entries.values('categories__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        most_common_categories = [
            {'name': item['categories__name'], 'count': item['count']}
            for item in category_counts if item['categories__name']
        ]
        
        # Racha de días consecutivos
        streak_days = self._calculate_streak(entries)
        
        # Favoritos
        favorite_entries = entries.filter(is_favorite=True).count()
        
        stats_data = {
            'total_entries': total_entries,
            'entries_this_month': entries_this_month,
            'entries_this_week': entries_this_week,
            'mood_distribution': mood_distribution,
            'average_intensity': round(avg_intensity, 2),
            'most_common_emotions': most_common_emotions,
            'most_common_categories': most_common_categories,
            'streak_days': streak_days,
            'favorite_entries': favorite_entries
        }
        
        serializer = EmotionalStatsSerializer(data=stats_data)
        serializer.is_valid()
        return Response(serializer.data)
    
    def _calculate_streak(self, entries):
        """Calcular racha de días consecutivos con entradas"""
        if not entries.exists():
            return 0
        
        dates = sorted(entries.values_list('entry_date', flat=True), reverse=True)
        if not dates:
            return 0
        
        streak = 1
        for i in range(len(dates) - 1):
            diff = (dates[i] - dates[i + 1]).days
            if diff == 1:
                streak += 1
            else:
                break
        
        return streak
    
    @action(detail=False, methods=['get'])
    def calendar_data(self, request):
        """
        Obtener datos para vista de calendario
        """
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        
        entries = self.get_queryset().filter(
            entry_date__year=year,
            entry_date__month=month
        )
        
        calendar_data = {}
        for entry in entries:
            date_str = entry.entry_date.isoformat()
            if date_str not in calendar_data:
                calendar_data[date_str] = []
            
            calendar_data[date_str].append({
                'id': str(entry.id),
                'title': entry.title,
                'mood': entry.mood,
                'intensity': entry.intensity
            })
        
        return Response(calendar_data)


class EmotionalMilestoneViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar hitos emocionales
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmotionalMilestoneSerializer
    
    def get_queryset(self):
        return EmotionalMilestone.objects.filter(user=self.request.user).select_related('user', 'entry')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EmotionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar emociones disponibles
    """
    permission_classes = [IsAuthenticated]
    queryset = emotions.objects.all()
    serializer_class = EmotionSerializer