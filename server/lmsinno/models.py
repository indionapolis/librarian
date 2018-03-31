from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

from django.utils.crypto import get_random_string

from rest_framework_jwt.settings import api_settings
from rest_framework.authtoken.models import Token

from . import const
from .tg_bot.engine import send_message

import datetime
import jwt
import re

jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class Document(models.Model):
    # Type of Documents:
    # 0 - Book; 1 - Journal article; 2 - AV
    DOCUMENT_TYPE_CHOICES = [(const.BOOK_TYPE, 'Book'),
                             (const.JOURNAL_TYPE, 'Journal article'),
                             (const.AV_TYPE, 'AV')]

    title = models.CharField(max_length=255)
    document_id = models.AutoField(primary_key=True, verbose_name=title)
    description = models.TextField(blank=True, max_length=10000)
    publisher = models.CharField(max_length=255)
    year = models.IntegerField(default=datetime.datetime.now().year)
    type = models.IntegerField(choices=DOCUMENT_TYPE_CHOICES)
    price = models.FloatField()
    is_reference = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    copies_available = models.IntegerField(default=0)
    cover = models.CharField(default='empty', max_length=1255)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    def take_copy(self):

        copies = Copy.objects.filter(document=self).filter(status=const.NOT_ORDERED_STATUS)

        if not copies:
            return None

        copy = copies.first()

        copy.status = const.ORDERED_STATUS
        copy.save()

        self.copies_available = len(Copy.objects.filter(document=self).filter(status=const.NOT_ORDERED_STATUS))
        self.save()

        return copy

    def return_copy(self, copy):
        if not copy:
            return
        if copy.document != self:
            return
        if copy.status == const.NOT_ORDERED_STATUS:
            return

        copy.status = const.NOT_ORDERED_STATUS
        copy.save()

        self.copies_available = len(Copy.objects.filter(document=self).filter(status=const.NOT_ORDERED_STATUS))
        self.save()

        Order.queue_validation()


class User(AbstractUser):
    # Type of User:
    # 0 - basic user; 1 - Faculty; 2 - Librarian
    USER_TYPE_CHOICES = [(const.BASIC_USER_ROLE, 'Basic user'),
                         (const.INSTRUCTOR_ROLE, 'Instructor'),
                         (const.TEACHER_ASSISTANT_ROLE, 'Teacher Assistant'),
                         (const.VISITING_PROFESSOR_ROLE, 'Visiting Professor'),
                         (const.PROFESSOR_ROLE, 'Professor'),
                         (const.LIBRARIAN_ROLE, 'Librarian')]

    role = models.IntegerField(default=const.BASIC_USER_ROLE, choices=USER_TYPE_CHOICES)
    address = models.CharField(max_length=100, default='innopolis')
    phone = models.DecimalField(unique=True, default=0, max_digits=11, decimal_places=0)
    telegram_id = models.IntegerField(default=0)

    def __str__(self):
        return '{0}'.format(self.username)

    def set_role(self, role):
        self.role = role

    def set_address(self, address):
        self.address = address

    def set_phone(self, phone):
        self.phone = phone

    def set_data(self, data):
        self.username = data.get('username') or self.username
        self.password = data.get('password1') or data.get('password') or self.password
        self.email = data.get('email') or self.email
        self.role = data.get('role') or self.role
        self.phone = data.get('phone') or self.phone
        self.address = data.get('address') or self.address
        self.last_name = data.get('last_name') or self.last_name
        self.first_name = data.get('first_name') or self.first_name

    def set_telegram_id(self, telegram_id):
        self.telegram_id = telegram_id
        self.save()

    @staticmethod
    def get_instance(request):
        if 'HTTP_HOST' in request.META:
            try:
                token = re.split(' ', request.META['HTTP_BEARER'])[1]
                payload = jwt.decode(token, settings.SECRET_KEY)
                email = payload['email']
                user_id = payload['user_id']

                user = User.objects.get(
                    email=email,
                    id=user_id
                )

            except jwt.ExpiredSignature or jwt.DecodeError or jwt.InvalidTokenError:
                return None
            except User.DoesNotExist:
                return None
            except KeyError:
                return None
            # empty session catcher
            except jwt.DecodeError:
                return None

            return user
        else:
            return None


class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.name


class DocumentOfAuthor(models.Model):
    class Meta:
        db_table = 'lmsinno_document_of_author'

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING)

    def __str__(self):
        return '{0}: {1}'.format(self.document, self.author)


class Copy(models.Model):
    # Type of Order Status
    # 0 - not ordered; 1 - ordered
    ORDER_STATUS_TYPE_CHOICES = [(i, i) for i in range(2)]

    copy_id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, to_field='document_id')
    status = models.IntegerField(choices=ORDER_STATUS_TYPE_CHOICES, default=0)
    place_hall_number = models.IntegerField(null=False)
    place_shelf_letter = models.CharField(max_length=1, null=False)

    def __str__(self):
        return '{0}: {1}'.format(str(self.copy_id), self.document)


class Order(models.Model):
    # Type of Status:
    # 0 - in queue; 1 - booked; 2 - overdue; 3 - closed; 4 - extended
    STATUS_TYPE_CHOICES = [(const.IN_QUEUE_STATUS, 'In queue'),
                           (const.BOOKED_STATUS, 'Booked'),
                           (const.OVERDUE_STATUS, 'Overdue'),
                           (const.CLOSED_STATUS, 'Closed'), ]

    order_id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, default=None, null=True)
    copy = models.ForeignKey(Copy, on_delete=models.CASCADE, default=None, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_TYPE_CHOICES, default=const.IN_QUEUE_STATUS)

    # date when order was created
    date_created = models.DateField(auto_now_add=True)
    # data when copy was attach to the order
    date_attach = models.DateTimeField(default=None, null=True)
    # data when patron take his order
    date_accepted = models.DateField(default=None, null=True)
    # data when patron return his  order
    date_return = models.DateField(default=None, null=True)

    def __str__(self):
        return '{0}: {1}'.format(self.user, self.document)

    @staticmethod
    def overdue_validation():
        """

        :return:
        """
        orders = Order.objects.all().exclude(status=const.IN_QUEUE_STATUS).exclude(status=const.CLOSED_STATUS)

        for order in orders:

            if order.date_return:
                if order.date_return < datetime.date.today():
                    order.status = const.OVERDUE_STATUS
                    order.save()

        Order.queue_validation()

    @staticmethod
    def queue_overdue_validation():
        orders = Order.objects.filter(status=const.IN_QUEUE_STATUS).exclude(copy=None)

        now = datetime.datetime.now(datetime.timezone.utc)
        for order in orders:
            if (now - order.date_attach) > datetime.timedelta(hours=24):
                order.close()
                print('sorry, your order is closed')
                # TODO notification


    @staticmethod
    def queue_validation():
        queue = Order.get_queue()
        for order in queue:
            order.attach_copy()

    @staticmethod
    def get_queue():
        """
        method to get priority queue for document
        :return:
        """
        orders_in_queue = Order.objects.filter(status=const.IN_QUEUE_STATUS).filter(copy=None)

        # TODO priority queue for orders

        orders_in_queue = orders_in_queue.order_by('-user__role')
        orders_in_queue = orders_in_queue.reverse()[::-1]

        return orders_in_queue

    @staticmethod
    def outstanding_request(document):
        orders = Order.objects.filter(document=document)
        orders = orders.filter(status=const.IN_QUEUE_STATUS)
        for order in orders:
            order.close()
            msg = 'Sorry, but the document ' + order.document.title + \
                  ' that you requested will not be available for checkout.' \
                  '\n' \
                  '\n' \
                  'You may be able to book the document soon.'
            send_message(order.user.telegram_id, msg)

    def attach_copy(self):
        """
        attach copy to the order if exist available copy
        :return:
        """
        if self.status != const.IN_QUEUE_STATUS:
            return
        if self.copy:
            return

        copy = self.document.take_copy()

        if copy:
            self.date_attach = datetime.datetime.today()
            self.copy = copy
            self.save()

            # notification
            msg = "Dear " + self.user.first_name + ",\n\nThe document " + self.copy.document.title + " is now available to checkout."
            send_message(str(self.user.telegram_id), msg)

    def accept_booking(self):
        """
        accept order in queue if it has copy
        :return:
        """
        if self.status != const.IN_QUEUE_STATUS:
            return
        self.attach_copy()
        if not self.copy:
            return

        self.date_accepted = datetime.date.today()
        delta = datetime.timedelta(days=1)

        # books are checked out for three weeks
        if self.user.role == const.BASIC_USER_ROLE:
            delta = datetime.timedelta(weeks=3)

        # current best sellers, in which case the limit is two weeks
        if self.copy.document.is_bestseller:
            delta = datetime.timedelta(weeks=2)

        # checked out by a faculty member, in which case the limit is 4 weeks
        if self.user.role == (const.LIBRARIAN_ROLE or
                              const.VISITING_PROFESSOR_ROLE or
                              const.TEACHER_ASSISTANT_ROLE or
                              const.INSTRUCTOR_ROLE or
                              const.PROFESSOR_ROLE):
            delta = datetime.timedelta(weeks=4)

        # AV materials and journals may be checked out for two weeks.
        if self.copy.document.type == (const.JOURNAL_TYPE or const.AV_TYPE):
            delta = datetime.timedelta(weeks=2)

        # Visiting Professor - limit is 1 week (regardless the type of the document)
        if self.user.role == const.VISITING_PROFESSOR_ROLE:
            delta = datetime.timedelta(weeks=1)

        self.date_return = datetime.date.today() + delta

        self.status = const.BOOKED_STATUS
        self.save()

    def renew(self):
        """

        :return:
        """
        if not self.is_renewable:
            return

        self.status = const.CLOSED_STATUS
        self.date_return = datetime.date.today()
        self.save()

        new_order = Order.objects.create(
            document=self.document,
            user=self.user,
            copy=self.copy
        )

    def close(self):
        """
        method to close unclosed order and return copy
        :return: overdue sum if any
        """
        if self.status == const.CLOSED_STATUS:
            return None

        overdue_sum = 0
        if self.status == const.OVERDUE_STATUS:
            overdue_days = (datetime.date.today() - self.date_return).days
            overdue_sum = min(overdue_days * 100, self.copy.document.price)

        # if order closed immediately copies number must no change
        if self.status != const.IN_QUEUE_STATUS:
            self.date_return = datetime.date.today()

        self.document.return_copy(self.copy)
        self.status = const.CLOSED_STATUS
        self.save()

        return overdue_sum

    def get_overdue_sum(self):
        pass

    def is_renewable(self):
        """
        method to check is it possible to renew an item
        :return:
        """
        if self.status == const.OVERDUE_STATUS:
            return False

        if not self.document.copies_available:
            orders_on_copy = Order.objects.filter(status=const.IN_QUEUE_STATUS)
            orders_on_copy = orders_on_copy.filter(document=self.document).filter(copy=None)
            if orders_on_copy:
                return False

        return True


class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class TagOfDocument(models.Model):
    class Meta:
        db_table = 'lmsinno_tag_of_document'

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return '{0}: {1}'.format(self.document, self.tag)



