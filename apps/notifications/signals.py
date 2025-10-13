from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from apps.community.models import Post, Community
from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_notification_via_websocket(user_id, notification_data):
    """
    Enviar notificación a través de WebSocket
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "notification_message",
            "notification": notification_data
        }
    )


@receiver(post_save, sender=Post)
def notify_community_members_new_post(sender, instance, created, **kwargs):
    """
    Notificar a todos los miembros de una comunidad cuando hay un nuevo post
    (excepto al autor)
    """
    if created and not instance.parent_post:  # Solo posts principales, no respuestas
        community = instance.community
        author = instance.author
        
        # Obtener todos los miembros excepto el autor
        members = community.users.exclude(id=author.id)
        
        for member in members:
            # Crear notificación
            notification = Notification.objects.create(
                recipient=member,
                sender=author,
                notification_type='new_post',
                title=f'Nuevo post en {community.name}',
                message=f'{author.username} publicó: {instance.title}',
                community=community,
                post=instance,
                redirect_url=f'/communities?community={community.id}&post={instance.id}'
            )
            
            # Enviar por WebSocket
            send_notification_via_websocket(member.id, notification.to_dict())


@receiver(post_save, sender=Post)
def notify_parent_post_author_reply(sender, instance, created, **kwargs):
    """
    Notificar al autor del post original cuando alguien responde
    """
    if created and instance.parent_post:
        parent_author = instance.parent_post.author
        reply_author = instance.author
        
        # No notificar si el autor se responde a sí mismo
        if parent_author.id != reply_author.id:
            notification = Notification.objects.create(
                recipient=parent_author,
                sender=reply_author,
                notification_type='post_reply',
                title='Nueva respuesta a tu post',
                message=f'{reply_author.username} respondió: {instance.text[:50]}...',
                community=instance.community,
                post=instance,
                redirect_url=f'/communities?community={instance.community.id}&post={instance.id}'
            )
            
            send_notification_via_websocket(parent_author.id, notification.to_dict())


@receiver(m2m_changed, sender=Post.likes.through)
def notify_post_like(sender, instance, action, pk_set, **kwargs):
    """
    Notificar al autor del post cuando alguien da like
    """
    if action == 'post_add':
        post = instance
        author = post.author
        
        # Obtener el usuario que dio like
        from apps.users.models import User
        liker = User.objects.filter(pk__in=pk_set).first()
        
        if liker and liker.id != author.id:
            notification = Notification.objects.create(
                recipient=author,
                sender=liker,
                notification_type='post_like',
                title='Like en tu post',
                message=f'A {liker.username} le gustó tu post: {post.title}',
                community=post.community,
                post=post,
                redirect_url=f'/communities?community={post.community.id}&post={post.id}'
            )
            
            send_notification_via_websocket(author.id, notification.to_dict())


@receiver(m2m_changed, sender=Community.users.through)
def notify_community_owner_new_member(sender, instance, action, pk_set, **kwargs):
    """
    Notificar al propietario de la comunidad cuando alguien se une
    """
    if action == 'post_add':
        community = instance
        owner = community.owner
        
        if owner:
            from apps.users.models import User
            new_member = User.objects.filter(pk__in=pk_set).first()
            
            if new_member and new_member.id != owner.id:
                notification = Notification.objects.create(
                    recipient=owner,
                    sender=new_member,
                    notification_type='community_join',
                    title=f'Nuevo miembro en {community.name}',
                    message=f'{new_member.username} se unió a tu comunidad',
                    community=community,
                    redirect_url=f'/communities?community={community.id}'
                )
                
                send_notification_via_websocket(owner.id, notification.to_dict())