from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import routers

from social_network.models import UserProfile, Post
from social_network.serializers import SignUpSerializer, UserProfileSerializer, PostSerializer
from social_network.permissions import UserIsOwner
from social_network.utils import get_info_from_clearbit
from social_network.constants import USE_CLEARBIT


# used GenericAPIView instead of APIView, because GenericAPIView generates swagger docs
class UserSignUp(GenericAPIView):
    serializer_class = SignUpSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.data.pop('confirm_password')
        if USE_CLEARBIT:
            user_info = {**get_info_from_clearbit(request.data['email']), **request.data}
        else:
            user_info = request.data
        model_serializer = UserProfileSerializer(data=user_info)
        model_serializer.is_valid(raise_exception=True)
        UserProfile.objects.create_user(**user_info)
        return Response(model_serializer.data)


class UserViewSet(ModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    permission_classes = (IsAuthenticated, UserIsOwner)


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        request.data.update({'user': request.user.id})
        return super(PostViewSet, self).create(request, *args, **kwargs)

    @action(detail=True, methods=['POST'])
    def like_dislike(self, request, *args, **kwargs):
        post_id = kwargs.pop('pk')
        action_type = request.data.get('action_type', None)
        if not action_type:
            return Response({'message': 'Should provide action type'})

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'message': 'No such post'})
        else:
            if action_type == 'like':
                post.like += 1
            elif action_type == 'dislike':
                post.dislike += 1
            post.save()
            return Response({'message': '''%s is set to %s's post''' % (action_type,
                                                                        post.user.username)})


router = routers.DefaultRouter()
router.register(r'post', PostViewSet)
router.register(r'user', UserViewSet)
urlpatterns = router.urls
