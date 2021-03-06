from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from . import copies_log_msg
from .copies_serializers import CopySerializer, CopyDetailSerializer
from .. import const
from ..permissions import permission_0, permission_2, permission_3, permission_1
from ..models import Copy, Document, Order, User
from ..logging.engine import make_log_record


class CopyDetail(APIView):
    """
    Class handle with copies
    """

    @staticmethod
    @permission_1
    def get(request, copy_id):
        """
        Get Copy bi ID
        :param request:
        :param copy_id:
        :return: HTTP_200_OK and JSON-Copy: copy with such ID exists
                 HTTP_404_NOT_FOUND and JSON: copy with with such ID does not exist
        """

        result = {'status': '', 'data': {}}

        log_record = {'user': User.get_instance(request).id,
                      'log_msg_type': 0,
                      'method_type': 0,
                      'params': {'copy_id': copy_id},
                      'response_status': status.HTTP_200_OK,
                      'description': copies_log_msg.get_copy_by_id}

        try:
            copy = Copy.objects.get(pk=copy_id)
        except Copy.DoesNotExist:
            log_record['log_msg_type'] = 2
            log_record['response_status'] = status.HTTP_404_NOT_FOUND
            make_log_record(**log_record)
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        serializer = CopyDetailSerializer(copy)

        result['data'] = serializer.data

        make_log_record(**log_record)
        return Response(result, status=status.HTTP_200_OK)

    @staticmethod
    @permission_2
    def post(request):
        """
        Add one particular copy
        :param request:
        :return: HTTP_200_OK and JSON-Copy: if copy was added successfully
                 HTTP_400_BAD_REQUEST: if format of input is wrong
        """

        result = {'status': '', 'data': {}}

        log_record = {'user': User.get_instance(request).id,
                      'log_msg_type': 0,
                      'method_type': 3,
                      'params': request.data,
                      'response_status': status.HTTP_200_OK,
                      'description': copies_log_msg.post_copy}

        serializer = CopySerializer(data=request.data)

        if serializer.is_valid():
            copy = serializer.save()
            Order.queue_validation()

            document = Document.objects.get(pk=copy.document_id)
            document.copies_available = Copy.objects.filter(document=document).filter(status=const.NOT_ORDERED_STATUS).count()
            document.save()

            result['data'] = CopyDetailSerializer(Copy.objects.get(pk=copy.pk)).data

            make_log_record(**log_record)
            return Response(result, status=status.HTTP_200_OK)

        result['data'] = serializer.errors

        log_record['log_msg_type'] = 2
        log_record['response_status'] = status.HTTP_400_BAD_REQUEST
        make_log_record(**log_record)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    @permission_3
    def delete(request, copy_id):
        """
        Delete Copy bi ID
        :param request:
        :param copy_id: document id in real
        :return: HTTP_200_OK and JSON-Copy: if deleted
                 HTTP_404_NOT_FOUND: no copes or document DoesNotExist
        """

        result = {'status': '', 'data': {}}

        log_record = {'user': User.get_instance(request).id,
                      'log_msg_type': 0,
                      'method_type': 2,
                      'params': {'copy_id': copy_id},
                      'response_status': status.HTTP_200_OK,
                      'description': copies_log_msg.delete_copy_by_id}

        try:
            document = Document.objects.get(document_id=copy_id)
            if not document.delete_copy():
                result['data'] = 'no copy to delete'
                log_record['log_msg_type'] = 2
                log_record['response_status'] = status.HTTP_404_NOT_FOUND
                make_log_record(**log_record)
                return Response(result, status=status.HTTP_404_NOT_FOUND)

        except Document.DoesNotExist:
            log_record['log_msg_type'] = 2
            log_record['response_status'] = status.HTTP_404_NOT_FOUND
            make_log_record(**log_record)
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        make_log_record(**log_record)
        return Response(result, status=status.HTTP_200_OK)