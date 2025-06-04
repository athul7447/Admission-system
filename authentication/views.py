from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

class LoginView(APIView):

    def post(self, request):
        """
        Handle POST request to authenticate user and obtain access token.

        Args:
            request: A rest_framework request object.

        Returns:
            A rest_framework response object with an access token and a refresh
            token if the authentication is successful, otherwise an appropriate
            error response.

        Raises:
            Exception: If there is any unhandled exception during the execution of
            this method.
        """
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            #validate the username and password
            if not username or not password:
                return Response(
                    {
                        "message": "Please provide both username and password",
                        "status":False,
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Authenticate the user
            user = authenticate(username=username, password=password)
            if user is not None:

                #check user is active
                if not user.is_active:
                    return Response(
                        {
                            "message": "User is inactive",
                            "status":False
                        },
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                # Generate tokens
                refresh = RefreshToken.for_user(user)

                return Response(
                    {
                        "access_token": str(refresh.access_token),
                        "message":"Login successful",
                        "status":True
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "message": "Invalid credentials",
                        "status":False
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            return Response(
                {
                    "message": str(e),
                    "status":False
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )