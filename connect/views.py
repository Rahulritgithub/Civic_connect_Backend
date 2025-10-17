import json
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token  
from connect.models import Post
from connect.serializers import UserRegistrationSerializer, UserLoginSerializer, PostQuerySerializer
from rest_framework.permissions import IsAuthenticated 
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt



##################################### User_Resgistration########################################
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'User registered successfully',
                'user_id': user.id,
                'email': user.email,
                'name': user.name,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


#####################################Login_User############################################

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    if request.method == 'POST':
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'email': user.email,
                'name': user.name,  # Use user.name instead of user.username
                'token': token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    


##################################### Post_query ########################################

@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])

def post_query(request):
    if request.method == 'GET':
        # Get posts for the authenticated user
        posts = Post.objects.filter(user=request.user).order_by('-created_at')
        serializer = PostQuerySerializer(posts, many=True)
        
        return Response({
            'success': True,
            'posts': serializer.data,
            'count': posts.count()
        }, status=status.HTTP_200_OK)
    

    elif request.method == 'POST':
        print("Received data:", request.data)
        print("Received FILES:", request.FILES)
        
        serializer = PostQuerySerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                post = serializer.save()
                print("Post saved successfully:", post.id)
                
                return Response({
                    'success': True,
                    'message': 'Post created successfully!',
                    'post_id': post.id,
                    'data': PostQuerySerializer(post).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                print(f"Error saving post: {str(e)}")
                import traceback
                traceback.print_exc()
                
                return Response({
                    'success': False,
                    'error': f'Failed to create post: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        else:
            print("Serializer errors:", serializer.errors)
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['GET'])
@permission_classes([AllowAny])
def view_all_posts(request):
    """
    Get all posts from all users
    """
    try:
        # Get all posts ordered by most recent first
        posts = Post.objects.all().order_by('-created_at')
        
        # Serialize the data
        serializer = PostQuerySerializer(posts, many=True)
        
        return Response({
            'success': True,
            'message': 'All posts retrieved successfully',
            'posts': serializer.data,
            'total_count': posts.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error retrieving all posts: {str(e)}")
        return Response({
            'success': False,
            'error': f'Failed to retrieve posts: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@require_http_methods(["POST"])
@permission_classes([IsAuthenticated])
def toggle_vote(request, post_id):
    """API endpoint to toggle vote"""
    try:
        post = Post.objects.get(id=post_id)
        success, vote_count = post.toggle_vote(request.user)
        user_has_voted = post.user_has_voted(request.user)
        
        return JsonResponse({
            'success': success,
            'vote_count': vote_count,
            'user_has_voted': user_has_voted,
            'post_id': post_id
        })
        
    except Post.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Post not found'
        }, status=404)
    
@csrf_exempt
@require_http_methods(["POST"])
@permission_classes([AllowAny])  # Allow unauthenticated access
def public_toggle_vote(request, post_id):
    """Public vote endpoint for testing - no authentication required"""
    try:
        post = Post.objects.get(id=post_id)
        
        # For testing, simulate a vote without requiring a user
        # You can modify this logic based on your needs
        data = json.loads(request.body)
        vote_action = data.get('vote', True)
        
        if vote_action:
            post.votes += 1
        else:
            post.votes = max(0, post.votes - 1)
        
        post.save()
        
        return JsonResponse({
            'success': True,
            'vote_count': post.votes,
            'user_has_voted': vote_action,
            'post_id': post_id,
            'message': 'Vote recorded successfully'
        })
        
    except Post.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Post not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    

@require_http_methods(["GET"])
@permission_classes([AllowAny])
def vote_status(request, post_id):
    """Get current vote status (public endpoint)"""
    try:
        post = Post.objects.get(id=post_id)
        vote_count = post.votes_count
        
        # Check if current user has voted
        user_has_voted = False
        if request.user.is_authenticated:
            user_has_voted = post.user_has_voted(request.user)
        
        return JsonResponse({
            'success': True,
            'vote_count': vote_count,
            'user_has_voted': user_has_voted,
            'is_authenticated': request.user.is_authenticated,
            'post_id': post_id
        })
        
    except Post.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Post not found'
        }, status=404)



