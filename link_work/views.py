from django.core.mail import send_mail
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, MagicLink
from .serializers import LoginSerializer, RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .utils import generate_jwt_token
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
            except Exception as e:
                return Response(
                    {"error": f"User creation failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            if not isinstance(user, CustomUser):
                return Response(
                    {"error": "User creation failed. Invalid user instance."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            magic_link = MagicLink.objects.create(user=user)
            link = f"http://yourdomain.com/auth/magic-link/{magic_link.token}/"

            send_mail(
                subject="Your Magic Login Link",
                message=f"Click the link to log in: {link}",
                from_email="no-reply@yourdomain.com",
                recipient_list=[user.email],
            )

            return Response(
                {"message": "User created successfully and magic link sent to email."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise Http404("User not found")

        magic_link = MagicLink.objects.create(user=user)
        link = f"http://yourdomain.com/auth/magic-link/{magic_link.token}/"

        send_mail(
            subject="Your Magic Login Link",
            message=f"Click the link to log in: {link}",
            from_email="no-reply@yourdomain.com",
            recipient_list=[email],
        )

        return Response(
            {"message": "A login link has been sent to your email."},
            status=status.HTTP_200_OK
        )

class MagicLinkAuthView(APIView):
    def get(self, request, token):
        try:
            magic_link = MagicLink.objects.get(token=token)
        except MagicLink.DoesNotExist:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        if not magic_link.is_valid():
            return Response({"error": "Magic link has expired."}, status=status.HTTP_400_BAD_REQUEST)

        user = magic_link.user
        magic_link.delete()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response(
            {"message": f"Welcome, {user.email}!", "jwt_token": access_token},
            status=status.HTTP_200_OK
        )




from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed

class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("Authorization Header:", request.headers.get('Authorization'))
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }, status=status.HTTP_200_OK)



class LogoutView(APIView):
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({"error": "Authorization token not provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return Response({"error": "Invalid Authorization header format"}, status=status.HTTP_400_BAD_REQUEST)

        cache.set(token, 'blacklisted', timeout=3600)

        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
