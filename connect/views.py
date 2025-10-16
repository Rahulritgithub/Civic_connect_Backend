from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token  
from django.contrib.auth import login, logout
from connect.models import Post
from connect.serializers import UserRegistrationSerializer, UserLoginSerializer, PostQuerySerializer
from rest_framework.permissions import IsAuthenticated 



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



