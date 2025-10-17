# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Post

class VoteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.room_group_name = f'post_{self.post_id}_votes'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            user = self.scope['user']
            
            if isinstance(user, AnonymousUser):
                await self.send(json.dumps({
                    'type': 'error',
                    'message': 'Please login to vote'
                }))
                return
            
            if action == 'toggle_vote':
                success, vote_count, user_has_voted = await self.toggle_vote(user, self.post_id)
                
                if success:
                    # Broadcast to ALL connected clients
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'vote_update',
                            'vote_count': vote_count,
                            'user_id': user.id,
                            'user_has_voted': user_has_voted,
                            'username': user.username
                        }
                    )
            
        except Exception as e:
            await self.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def vote_update(self, event):
        """Send real-time update to ALL clients"""
        await self.send(text_data=json.dumps({
            'type': 'vote_update',
            'vote_count': event['vote_count'],
            'user_id': event['user_id'],
            'user_has_voted': event['user_has_voted'],
            'username': event['username']
        }))
    
    @database_sync_to_async
    def toggle_vote(self, user, post_id):
        """Toggle vote for authenticated user"""
        try:
            post = Post.objects.get(id=post_id)
            success, vote_count = post.toggle_vote(user)
            user_has_voted = post.user_has_voted(user)
            return success, vote_count, user_has_voted
        except Post.DoesNotExist:
            return False, 0, False
        except Exception as e:
            return False, 0, False