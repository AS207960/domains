from django.core.management.base import BaseCommand
from domains import apps, models
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.core import mail
import domains.epp_api.epp_grpc.epp_pb2
import domains.epp_api.epp_grpc.epp_pb2_grpc
import domains.epp_api.epp_grpc.common.common_pb2
import google.protobuf.json_format
import grpc
import email.utils
import json
from domains.views import emails
from domains import tasks

REGISTRY_CLIENT_IDS = {
    "rrpproxy": "as207960",
    "id": "ascy-802642"
}

class Command(BaseCommand):
    help = "Polls and handles any pending messages from registries"

    def add_arguments(self, parser):
        parser.add_argument("registry", nargs="+", type=str)

    def handle(self, *args, **options):
        for r in options["registry"]:
            self.poll_registry(r)

    def poll_registry(self, registry_name: str):
        print(f"Polling {registry_name}", flush=True)
        while True:
            try:
                resp: apps.epp_api.epp_pb2.PollReply = apps.epp_client.stub.PollSingle(apps.epp_api.epp_pb2.RegistryInfo(
                    registry_name=registry_name
                ))
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.RESOURCE_EXHAUSTED:
                    break
                raise e

            self.callback(resp, registry_name)

            ack_resp: apps.epp_api.epp_pb2.PollAckReply = apps.epp_client.stub.AckPoll(apps.epp_api.epp_pb2.PollAckSingle(
                msg_id=resp.msg_id,
                registry_name=registry_name
            ))
            print(f"{ack_resp.count} messages remaining on {registry_name}", flush=True)
            if ack_resp.count == 0:
                break

        print(f"Done with {registry_name}", flush=True)

    def callback(self, m: domains.epp_api.epp_grpc.epp_pb2.PollReply, registry_name: str):
        if m.HasField("change_data") and m.WhichOneof("data") == "domain_info":
            self.handle_domain_update(m)
        elif m.WhichOneof("data") == "nominet_domain_release":
            self.handle_nominet_domain_release(m)
        elif m.WhichOneof("data") == "nominet_domain_registrar_change":
            self.handle_nominet_domain_registrar_change(m, registry_name)
        elif m.WhichOneof("data") == "nominet_domain_cancel":
            self.handle_nominet_domain_cancel(m)
        elif m.WhichOneof("data") == "domain_transfer":
            self.handle_domain_transfer(m, registry_name)
        elif m.WhichOneof("data") == "eurid_poll":
            self.handle_eurid_poll(m)

        m_data = google.protobuf.json_format.MessageToDict(
            m, always_print_fields_with_no_presence=True
        )
        json_data = json.dumps(m_data, indent=4, sort_keys=True)

        mail.EmailMessage(
            to=["noc@as207960.net"],
            from_email=settings.DEFAULT_FROM_EMAIL,
            subject=f"EPP Poll Notification - {registry_name}",
            body=f"<p><pre>{json_data}</pre></p>",
            headers={
                "Content-Type": "text/html",
                "Date": email.utils.format_datetime(m.enqueue_date.ToDatetime())
            },
        ).send()

    def handle_domain_update(self, m):
        domain = apps.epp_api.Domain.from_pb(m.domain_info, apps.epp_client)
        change_data = apps.epp_api.ChangeData.from_pb(m.change_data)

        domain_obj = models.DomainRegistration.objects.filter(domain__iexact=domain.name).first()
        if not domain_obj:
            print(f"Unknown domain: {domain.name}", flush=True)
            return

        user = domain_obj.get_user()
        if user:
            domain_url = settings.EXTERNAL_URL_BASE + reverse('domain', args=(domain_obj.id,))

            emails.send_email(user, {
                "subject": "Domain updated by registry",
                "content": render_to_string("domains_email/registry_update.html", {
                    "domain": domain_obj.unicode_domain,
                    "domain_data": domain,
                    "domain_url": domain_url,
                    "change_data": change_data,
                })
            }, extra_headers={
                "Date": email.utils.format_datetime(m.enqueue_date.ToDatetime())
            })

    def handle_nominet_domain_release(self, m):
        for domain in m.nominet_domain_release.domains:
            domain_obj = models.DomainRegistration.objects.filter(domain__iexact=domain).first()
            if not domain_obj:
                print(f"Unknown domain: {domain}", flush=True)
                return

            domain_obj.former_domain = True
            domain_obj.save()
            emails.mail_transferred_out.delay(domain_obj.id)

    def handle_nominet_domain_registrar_change(self, m, registry_name: str):
        for domain in m.nominet_domain_registrar_change.domains:
            domain_transfer_order = models.DomainTransferOrder.objects.filter(domain__iexact=domain.name).first()
            if domain.client_id != m.nominet_domain_registrar_change.registrar_tag:
                if m.nominet_domain_registrar_change.case_id:
                    try:
                        if domain_transfer_order:
                            apps.epp_client.stub.NominetAccept(apps.epp_api.nominet_pb2.HandshakeAcceptRequest(
                                case_id=m.nominet_domain_registrar_change.case_id.value,
                                registry_name=registry_name,
                            ))
                        else:
                            apps.epp_client.stub.NominetReject(apps.epp_api.nominet_pb2.HandshakeRejectRequest(
                                case_id=m.nominet_domain_registrar_change.case_id.value,
                                registry_name=registry_name,
                            ))
                    except grpc.RpcError as e:
                        print(f"Can't action pending transfer for {domain.name}: {e.details()}")
                        return
            else:
                if not domain_transfer_order:
                    print(f"Unknown domain transfer: {m.domain_transfer.name}", flush=True)
                    return
                tasks.process_domain_transfer_complete.delay(domain_transfer_order.id)

    def handle_nominet_domain_cancel(self, m):
        domain_obj = models.DomainRegistration.objects.filter(domain__iexact=m.nominet_domain_cancel.name).first()
        if not domain_obj:
            print(f"Unknown domain: {m.nominet_domain_cancel.name}", flush=True)
            return

        domain_obj.former_domain = True
        domain_obj.save()

    def handle_domain_transfer(self, m, registry_name: str):
        if registry_name in REGISTRY_CLIENT_IDS:
            if m.domain_transfer.requested_client_id == REGISTRY_CLIENT_IDS[registry_name]:
                self.handle_domain_transfer_in(m)
            else:
                self.handle_domain_transfer_out(m)

    def handle_domain_transfer_in(self, m):
        domain_transfer_order = models.DomainTransferOrder.objects.filter(domain__iexact=m.domain_transfer.name).first()
        if not domain_transfer_order:
            print(f"Unknown domain transfer: {m.domain_transfer.name}", flush=True)
            return

        if m.domain_transfer.status == domains.epp_api.epp_grpc.common.common_pb2.ServerApproved or \
            m.domain_transfer.status == domains.epp_api.epp_grpc.common.common_pb2.ClientApproved:
            tasks.process_domain_transfer_complete.delay(domain_transfer_order.id)
        elif m.domain_transfer.status == domains.epp_api.epp_grpc.common.common_pb2.ServerCancelled or \
            m.domain_transfer.status == domains.epp_api.epp_grpc.common.common_pb2.ClientCancelled or \
            m.domain_transfer.status == domains.epp_api.epp_grpc.common.common_pb2.ClientRejected:
            tasks.process_domain_transfer_failed.delay(domain_transfer_order.id)

    def handle_domain_transfer_out(self, m):
        domain_obj = models.DomainRegistration.objects.filter(domain__iexact=m.domain_transfer.name).first()
        if not domain_obj:
            print(f"Unknown domain: {m.domain_transfer.name}", flush=True)
            return

        if m.domain_transfer.status == domains.epp_api.epp_grpc.common.common_pb2.Pending:
            domain_obj.transfer_out_pending = True
            domain_obj.save()
            emails.mail_transfer_out_request.delay(domain_obj.id)
        elif m.domain_transfer.status == domains.epp_api.epp_grpc.common.common_pb2.ServerApproved or \
            m.domain_transfer.status == domains.epp_api.epp_grpc.common.common_pb2.ClientApproved:
            domain_obj.former_domain = True
            domain_obj.save()
            emails.mail_transferred_out.delay(domain_obj.id)
        elif m.domain_transfer.status == domains.epp_api.epp_grpc.common.common_pb2.ServerCancelled or \
            m.domain_transfer.status == domains.epp_api.epp_grpc.common.common_pb2.ClientCancelled or \
            m.domain_transfer.status == domains.epp_api.epp_grpc.common.common_pb2.ClientRejected:
            domain_obj.transfer_out_pending = False
            domain_obj.save()

    def handle_eurid_poll(self, m):
        if m.eurid_poll.context == "TRANSFER" and m.eurid_poll.action == "AWAY" and m.eurid_poll.object_type == "DOMAIN":
            domain_obj = models.DomainRegistration.objects.filter(domain__iexact=m.eurid_poll.object).first()
            if not domain_obj:
                print(f"Unknown domain: {m.eurid_poll.object}", flush=True)
                return
            domain_obj.former_domain = True
            domain_obj.save()
            emails.mail_transferred_out.delay(domain_obj.id)
