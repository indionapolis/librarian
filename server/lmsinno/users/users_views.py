from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .users_serializers import UserResponseDataSerializer, UserDetailSerializer
from .. import misc
from ..models import User
from ..permissions import LibrariantPermission, UserDetailPermission


class Users(APIView):
    """
       Class to get list of all Users
    """
    permission_classes = (LibrariantPermission,)

    @staticmethod
    def get(request):
        """
            GET request to get list of all Users
            :param request:
            :return: HTTP_200_OK and JSON-Documents: if all good
                     HTTP_404_NOT_FOUND: if users don`t exist
        """
        result = {'status': '', 'data': {}}

        if not User.objects.all():
            result['status'] = misc.HTTP_404_NOT_FOUND
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        serializer = UserResponseDataSerializer(User.objects.all(), many=True)
        result['data'] = serializer.data
        result['status'] = misc.HTTP_200_OK

        return Response(result, status=status.HTTP_200_OK)


class UserDetail(APIView):
    """
        Class to get one User by id
    """
    permission_classes = (UserDetailPermission,)

    @staticmethod
    def get(request, user_id):
        """
            GET request to get one particular user
            :param request:
            :param user_id
            :return: HTTP_200_OK and JSON-Documents: if all good
                    HTTP_404_NOT_FOUND: if user don`t exist
        """
        result = {'status': '', 'data': {}}

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            result['status'] = misc.HTTP_404_NOT_FOUND
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        serializer = UserDetailSerializer(user)
        result['data'] = serializer.data
        result['status'] = misc.HTTP_200_OK
        return Response(result, status=status.HTTP_200_OK)

    @staticmethod
    def patch(request, user_id):
        """
            PATCH request to update users
            :param request:
            :param user_id:
            :return: HTTP_202_ACCEPTED and JSON-Document: update is success
                     HTTP_400_BAD_REQUEST and JSON-Document with errors: data is not valid
                     HTTP_404_NOT_FOUND: user with such id is not found
        """

        result = {'status': '', 'data': {}}

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            result['status'] = misc.HTTP_404_NOT_FOUND
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        serializer = UserDetailSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            # First, need to check whether the user try to change his role
            # We return 'accepted' in case that 'hacker' who try to change state
            # Might try several times before he totally burn in tears about our security :)
            # NOTE: User.get_instance(request).role - the instance of requester
            if User.get_instance(request).role != 2 or (user.role != User.get_instance(request).role and User.get_instance(request).role != 2):
                return Response(result, status=status.HTTP_202_ACCEPTED)
            # If pass, then save all
            serializer.save()
            result['status'] = misc.HTTP_202_ACCEPTED
            return Response(result, status=status.HTTP_202_ACCEPTED)

        result['status'] = misc.HTTP_400_BAD_REQUEST
        result['data'] = serializer.errors

        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class MyDetail(APIView):
    """
        Class to get one User by id
    """
    permission_classes = (LibrariantPermission,)

    @staticmethod
    def get(request, user_id):
        """
            GET request to get one particular user
            :param request:
            :param user_id:
            :return: HTTP_200_OK and JSON-Documents: if all good
                    HTTP_404_NOT_FOUND: if user don`t exist
        """
        result = {'status': '', 'data': {}}

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            result['status'] = misc.HTTP_404_NOT_FOUND
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        serializer = UserDetailSerializer(user)
        result['data'] = serializer.data
        result['status'] = misc.HTTP_200_OK
        return Response(result, status=status.HTTP_200_OK)
