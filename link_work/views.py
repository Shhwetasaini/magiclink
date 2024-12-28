from django.core.mail import send_mail
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, MagicLink
from .serializers import LoginSerializer, RegisterSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Attempt to create the user
            try:
                user = serializer.save()
            except Exception as e:
                return Response(
                    {"error": f"User creation failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Validate the user instance
            if not isinstance(user, CustomUser):
                return Response(
                    {"error": "User creation failed. Invalid user instance."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Create the MagicLink
            magic_link = MagicLink.objects.create(user=user)
            link = f"http://yourdomain.com/auth/magic-link/{magic_link.token}/"

            # Send the magic link via email
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

        # Create a MagicLink for the user
        magic_link = MagicLink.objects.create(user=user)
        link = f"http://yourdomain.com/auth/magic-link/{magic_link.token}/"

        # Send the magic link to the user's email
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

        # Authenticate the user (customize this behavior based on your application)
        user = magic_link.user
        magic_link.delete()  # Delete the magic link after successful use

        return Response(
            {"message": f"Welcome, {user.email}! You are successfully logged in."},
            status=status.HTTP_200_OK
        )
