from .models import Document, Author, DocumentOfAuthor, Tag
from .serializer import DocumentSerializer, AuthorSerializer, TagSerializer

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .misc import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_202_ACCEPTED

import re


class DocumentDetail(APIView):
    """
    Class to get one particular document by id
    """

    # TODO AUTHORIZATION
    def get(self, request, document_id, format=None):
        """
        GET request to get one particular document
        :param request:
        :param document_id:
        :return: HTTP_200_OK and JSON-Documents: if documents with such id exists
                 HTTP_404_NOT_FOUND: if document with such id doesn`t exist
        """

        result = {'status': '', 'data': {}}

        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            result['status'] = HTTP_404_NOT_FOUND
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentSerializer(document)
        result['status'] = HTTP_200_OK
        result['data'] = serializer.data

        return Response(result, status=status.HTTP_200_OK)


class DocumentsByCriteria(APIView):
    """
    Class to work with document using some criteria
    """

    # TODO AUTHORIZATION
    def get(self, request, format=None):
        """
        GET request to get set of document by criteria
        :param request:
        :return: HTTP_200_OK and JSON-Documents: if documents with such criteria exists
                 HTTP_404_NOT_FOUND: if documents with such criteria doesn`t exists
        """

        DEFAULT_SIZE = 50
        DEFAULT_OFFSET = 0

        result = {'status': '', 'data': {}}

        # If params are empty
        if not request.GET:
            result['status'] = HTTP_400_BAD_REQUEST
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        author_name = request.GET.get('author_name', None)
        title = request.GET.get('title', None)
        year = request.GET.get('year', None)
        tag_ids = request.GET.get('tag_ids', None)
        size = request.GET.get('size', None)
        offset = request.GET.get('offset', None)

        data_query_set = Document.objects

        if author_name is not None:
            author_name = author_name.strip()
            data_query_set = data_query_set.filter(documentofauthor__author__name__icontains=author_name)
        if title is not None:
            title = title.strip()
            data_query_set = data_query_set.filter(title__icontains=title)
        if year is not None:
            data_query_set = data_query_set.filter(year=year)
        if tag_ids is not None:
            tag_ids = re.sub('[ \[\]]', '', tag_ids).split(',')
            data_query_set = data_query_set.filter(tagofdocument__tag_id=tag_ids[0])
            for index in range(1, len(tag_ids)):
                data_query_set = data_query_set & data_query_set.filter(tagofdocument__tag_id=tag_ids[index])
        if size is not None or offset is not None:
            size = size if size else DEFAULT_SIZE
            offset = offset if offset else DEFAULT_OFFSET
            data_query_set = data_query_set.filter()[int(offset):int(offset) + int(size)]

        serializer = DocumentSerializer(data_query_set, many=True)

        result['data'] = serializer.data

        if serializer.data:
            result['status'] = HTTP_200_OK
            return Response(result, status=status.HTTP_200_OK)

        result['status'] = HTTP_404_NOT_FOUND
        return Response(result, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, format=None):
        """
        POST request: add one particular document
        :param request: input params
        :return: HTTP_202_ACCEPTED: if document was added successful
                 HTTP_400_BAD_REQUEST and JSON-errors: if wrong format of input data
        """

        doc_serializer = DocumentSerializer(data=request.data)

        if doc_serializer.is_valid() and request.POST.get('authors'):
            doc_obj = doc_serializer.save()

            authors_list = re.sub('[\[\]]', '', request.POST.get('authors'))
            authors_list = authors_list.split(',')

            for author in authors_list:
                author = author.strip()
                author_obj = Author.objects.filter(name=author).first()
                if not author_obj:
                    author_obj = Author.objects.create(name=author)
                DocumentOfAuthor.objects.create(document_id=doc_obj.document_id, author_id=author_obj.author_id)
            return Response({'status': HTTP_202_ACCEPTED, 'data': {}}, status=status.HTTP_202_ACCEPTED)

        return Response(doc_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # TODO AUTHORIZATION
        """
        DELETE request: delete one particular document by id
        :param request:
        :return: HTTP_200_OK: if document was deleted success
                 HTTP_404_NOT_FOUND: if document with such id not found
                 HTTP_400_BAD_REQUEST: if wrong format of input data
        """
        document_id = request.query_params.get('id')

        if document_id:
            try:
                document = Document.objects.get(pk=document_id)
            except Document.DoesNotExist:
                return Response({'status': HTTP_404_NOT_FOUND, 'data': {}}, status=status.HTTP_404_NOT_FOUND)
            serializer = DocumentSerializer(document)
            document.delete()
            return Response({'status': HTTP_200_OK, 'data': serializer.data})

        return Response({'status': HTTP_400_BAD_REQUEST, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)


class TagDetail(APIView):
    """
    Class to get one particular tag by ID
    """
    def get(self, request, tag_id, format=None):
        """
        Get one particular tag by ID
        :param request:
        :param tag_id:
        :param format:
        :return: HTTP_200_OK and JSON-tag: if tag with such ID exists
                 HTTP_404_NOT_FOUND and JSON: if tag with such doesn`t exist
        """

        result = {'status': '', 'data': {}}

        try:
            tag = Tag.objects.get(pk=tag_id)
        except Tag.DoesNotExist:
            result['status'] = HTTP_404_NOT_FOUND
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        tag_serializer = TagSerializer(tag)
        result['data'] = tag_serializer.data
        result['status'] = HTTP_200_OK

        return Response(result, status=status.HTTP_200_OK)
