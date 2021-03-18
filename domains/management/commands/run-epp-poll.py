from django.core.management.base import BaseCommand
from domains import apps, models
from django.conf import settings
from django.shortcuts import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import threading
import domains.epp_api.epp_grpc.epp_pb2
import domains.epp_api.epp_grpc.epp_pb2_grpc
import google.protobuf.json_format
import queue
import time
import grpc
import traceback
import json


class PollClient:
    def __init__(
            self, stub: domains.epp_api.epp_grpc.epp_pb2_grpc.EPPProxyStub, registry_name: str,
            callback, callback_exc=None
    ):
        self._stub = stub
        self._registry_name = str(registry_name)
        self._pending_ack = queue.Queue()
        self._callback = callback
        self._callback_exc = callback_exc
        self._exit = threading.Event()
        self._channel = None
        self._t = None

    def __iter__(self):
        return self

    def __next__(self):
        while (msg_id := self._pending_ack.get()) is None:
            time.sleep(0.1)

        return domains.epp_api.epp_grpc.epp_pb2.PollAck(
            msg_id=msg_id
        )

    def _run_iter(self):
        while not self._exit.isSet():
            self._channel = self._stub.Poll(
                self,
                metadata=(
                    ("registry_name", self._registry_name),
                )
            )
            try:
                for msg in self._channel:
                    try:
                        self._callback(self, msg)
                    except:
                        traceback.print_exc()
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.CANCELLED:
                    return
                elif e.code() == grpc.StatusCode.UNAVAILABLE:
                    pass
                else:
                    try:
                        self._callback_exc(self, e)
                    except:
                        traceback.print_exc()

            time.sleep(60)

    def _run_watcher(self):
        while not self._exit.isSet():
            if not self._t.is_alive():
                self._t = threading.Thread(target=self._run_iter)
                self._t.start()
            time.sleep(5)

    def run(self):
        self._t = threading.Thread(target=self._run_iter)
        t = threading.Thread(target=self._run_watcher)
        self._t.start()
        t.start()

    def exit(self):
        self._exit.set()
        if self._channel:
            self._channel.cancel()

    def ack(self, msg_id: str):
        self._pending_ack.put(str(msg_id))

    @property
    def registry_name(self):
        return self._registry_name


def mail_domain_change_poll(domain: models.DomainRegistration):
    user = domain.get_user()
    domain_url = settings.EXTERNAL_URL_BASE + reverse('domain', args=(domain.id,))
    context = {
        "name": user.first_name,
        "domain": domain.unicode_domain,
        "domain_url": domain_url,
    }
    html_content = render_to_string("domains_email/register_success.html", context)
    txt_content = render_to_string("domains_email/register_success.txt", context)

    email = EmailMultiAlternatives(
        subject='Domain updated by registry',
        body=txt_content,
        to=[user.email],
        bcc=['email-log@as207960.net'],
        reply_to=['Glauca Support <hello@glauca.digital>']
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


class Command(BaseCommand):
    help = 'Runs long running EPP poll commands and handles responses'

    def add_arguments(self, parser):
        parser.add_argument("registry", nargs="+", type=str)

    def handle(self, *args, **options):
        clients = []

        for r in options["registry"]:
            c = PollClient(apps.epp_client.stub, r, self.callback, self.callback_exc)
            print(f"Starting client for: {r}")
            c.run()
            clients.append(c)
        print("Poll handler running")
        try:
            while True:
                time.sleep(0.1)
        except (KeyboardInterrupt, SystemExit):
            print("Exiting...")
            for c in clients:
                c.exit()

    def callback(self, client: PollClient, m: domains.epp_api.epp_grpc.epp_pb2.PollReply):
        if m.HasField("change_data") and m.WhichOneof("data") == "domain_info":
            self.handle_domain_update(m)

        m_data = google.protobuf.json_format.MessageToDict(m, including_default_value_fields=True)
        json_data = json.dumps(m_data, indent=4, sort_keys=True)

        e_msg = EmailMultiAlternatives(
            subject=f"EPP Poll Notification - {client.registry_name}",
            body=json_data,
            to=["noc@as207960.net"]
        )
        e_msg.send()

        client.ack(m.msg_id)

    def callback_exc(self, client: PollClient, e):
        e_msg = EmailMultiAlternatives(
            subject=f"EPP Poll Exception - {client.registry_name}",
            body=str(e),
            to=["noc@as207960.net"]
        )
        e_msg.send()

    def handle_domain_update(self, m):
        domain = apps.epp_api.Domain.from_pb(m.domain_info, apps.epp_client)
        change_data = apps.epp_api.ChangeData.from_pb(m.change_data)

        domain_obj = models.DomainRegistration.objects.filter(domain=domain.name).first()
        if not domain_obj:
            print(f"Unknown domain: {domain.name}")
            return

        user = domain_obj.get_user()
        domain_url = settings.EXTERNAL_URL_BASE + reverse('domain', args=(domain_obj.id,))
        context = {
            "name": user.first_name,
            "domain": domain_obj.unicode_domain,
            "domain_data": domain,
            "domain_url": domain_url,
            "change_data": change_data,
            "subject": "Domain updated by registry"
        }
        html_content = render_to_string("domains_email/registry_update.html", context)
        txt_content = render_to_string("domains_email/registry_update.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain updated by registry',
            body=txt_content,
            to=[user.email],
            bcc=['email-log@as207960.net'],
            reply_to=['Glauca Support <hello@glauca.digital>']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
