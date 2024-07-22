from django.utils import timezone
import datetime
from . import apps, zone_info, models

NOTIFY_INTERVAL = datetime.timedelta(days=60)
RENEW_INTERVAL = datetime.timedelta(days=30)

def domain_paid_until_date(
        domain_obj: models.DomainRegistration, domain_data: apps.epp_api.Domain, domain_info: zone_info.DomainInfo
):
    now = timezone.now()

    if domain_data.paid_until_date:
        expiry_date = domain_data.paid_until_date.replace(tzinfo=datetime.timezone.utc) + domain_info.expiry_offset
    elif domain_data.expiry_date:
        expiry_date = domain_data.expiry_date.replace(tzinfo=datetime.timezone.utc) + domain_info.expiry_offset
    else:
        return None, None

    paid_up_until = None
    if expiry_date - RENEW_INTERVAL <= now:
        last_auto_renew_order = models.DomainAutomaticRenewOrder.objects.filter(domain_obj=domain_obj) \
            .order_by("-timestamp").first()  # type: models.DomainAutomaticRenewOrder
        if last_auto_renew_order and last_auto_renew_order.state == last_auto_renew_order.STATE_COMPLETED and \
                last_auto_renew_order.timestamp + NOTIFY_INTERVAL >= now:
            if last_auto_renew_order.period_unit == apps.epp_api.common_pb2.Period.Months:
                renew_period = datetime.timedelta(weeks=4 * last_auto_renew_order.period_value)
            else:
                renew_period = datetime.timedelta(weeks=52 * last_auto_renew_order.period_value)

            paid_up_until = expiry_date + renew_period
        else:
            last_restore_order = models.DomainRestoreOrder.objects.filter(domain_obj=domain_obj, should_renew=True) \
                .order_by("-timestamp").first()  # type: models.DomainRestoreOrder
            if last_restore_order and last_restore_order.state == last_restore_order.STATE_COMPLETED and \
                    last_restore_order.timestamp + NOTIFY_INTERVAL >= now:
                if last_restore_order.period_unit == apps.epp_api.common_pb2.Period.Months:
                    renew_period = datetime.timedelta(weeks=4 * last_restore_order.period_value)
                else:
                    renew_period = datetime.timedelta(weeks=52 * last_restore_order.period_value)

                paid_up_until = expiry_date + renew_period

    return expiry_date, paid_up_until