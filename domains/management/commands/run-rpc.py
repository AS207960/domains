from django.core.management.base import BaseCommand
from django.conf import settings
import pika
from domains import models, tasks
import domains.proto.billing_pb2


class Command(BaseCommand):
    help = 'Runs the RPC client on rabbitmq'

    def handle(self, *args, **options):
        parameters = pika.URLParameters(settings.RABBITMQ_RPC_URL)
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel()

        channel.queue_declare(queue='domains_registration_billing_notif', durable=True)
        channel.queue_declare(queue='domains_transfer_billing_notif', durable=True)
        channel.queue_declare(queue='domains_renew_billing_notif', durable=True)
        channel.queue_declare(queue='domains_auto_renew_billing_notif', durable=True)
        channel.queue_declare(queue='domains_restore_billing_notif', durable=True)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue='domains_registration_billing_notif',
            on_message_callback=self.domains_registration_callback,
            auto_ack=False
        )
        channel.basic_consume(
            queue='domains_transfer_billing_notif',
            on_message_callback=self.domains_transfer_callback,
            auto_ack=False
        )
        channel.basic_consume(
            queue='domains_renew_billing_notif',
            on_message_callback=self.domains_renew_callback,
            auto_ack=False
        )
        channel.basic_consume(
            queue='domains_auto_renew_billing_notif',
            on_message_callback=self.domains_auto_renew_callback,
            auto_ack=False
        )
        channel.basic_consume(
            queue='domains_restore_billing_notif',
            on_message_callback=self.domains_restore_callback,
            auto_ack=False
        )

        print("RPC handler now running")
        try:
            channel.start_consuming()
        except (KeyboardInterrupt, SystemExit):
            print("Exiting...")
            return

    def domains_callback(self, body, model, task, failed_task=None):
        msg = domains.proto.billing_pb2.ChargeStateNotification()
        msg.ParseFromString(body)

        order = model.objects.filter(charge_state_id=msg.charge_id).first()
        if not order:
            return
        last_error = msg.last_error.value if msg.HasField("last_error") else None

        if msg.state == domains.proto.billing_pb2.FAILED:
            order.state = order.STATE_FAILED
            order.last_error = last_error
            order.save()
            if failed_task:
                failed_task.delay(order.id)
        elif msg.state == domains.proto.billing_pb2.COMPLETED:
            if order.state in (order.STATE_PENDING, order.STATE_STARTED, order.STATE_NEEDS_PAYMENT):
                order.state = order.STATE_PROCESSING
                order.save()
                task.delay(order.id)
        elif msg.state in (
                domains.proto.billing_pb2.PENDING,
                domains.proto.billing_pb2.PROCESSING
        ):
            order.state = order.STATE_NEEDS_PAYMENT
            order.redirect_url = msg.redirect_url
            order.save()

    def domains_registration_callback(self, channel, method, properties, body):
        self.domains_callback(body, models.DomainRegistrationOrder, tasks.process_domain_registration_paid)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def domains_transfer_callback(self, channel, method, properties, body):
        self.domains_callback(body, models.DomainTransferOrder, tasks.process_domain_transfer_paid)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def domains_renew_callback(self, channel, method, properties, body):
        self.domains_callback(body, models.DomainRenewOrder, tasks.process_domain_renewal_paid)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def domains_auto_renew_callback(self, channel, method, properties, body):
        self.domains_callback(
            body, models.DomainAutomaticRenewOrder, tasks.process_domain_auto_renew_paid,
            tasks.emails.mail_auto_renew_failed
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def domains_restore_callback(self, channel, method, properties, body):
        self.domains_callback(body, models.DomainRestoreOrder, tasks.process_domain_restore_paid)
        channel.basic_ack(delivery_tag=method.delivery_tag)
