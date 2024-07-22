from rest_framework import generics, status,viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from authentication import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny
from django.contrib.auth import get_user_model
from utils.common_pagination import CustomPagination



class UserListCreateView(generics.ListCreateAPIView):
    serializer_class=serializers.UserSerializer
    queryset= get_user_model().objects.all()
    permission_classes=[IsAuthenticated]
    pagination_class=CustomPagination

class UserUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class=serializers.UserSerializer
    queryset= get_user_model().objects.all()
    permission_classes=[IsAuthenticated]


class LoginView(TokenObtainPairView):
    serializer_class=serializers.LoginSerializer

class ResetPasswordEmailRequest(APIView):
    serializer_class = serializers.ResetPasswordEmailRequestSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"message": "Password reset link sent.Please check your email "},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserPasswordResetView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, uid, token):
        serializer = serializers.UserPasswordResetViewSerializer(
            data={
                "uid": uid,
                "token": token,
                "new_password": request.data.get("new_password"),
            }
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({"message": "Password reset successfully"})
    

class UserChangePassword(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        serializer = serializers.UserChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"message": "Change Password Successfully "}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProfileGetUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        if request.user:
            serializer = serializers.ProfileUserSerializer(instance=request.user,context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_200_OK)
    def put(self, request, *args, **kwargs):
        if request.user:
            serializer = serializers.ProfileUserSerializer(instance=request.user, data=request.data,context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({
                    "message": "Profile Updated successfully",
                    "data": serializer.data,
                }, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_200_OK)

    

