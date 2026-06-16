import ipaddress

from django.conf import settings
from rest_framework.permissions import BasePermission

_LOOPBACK = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
]


def _parse_networks(cidrs):
    return [ipaddress.ip_network(c, strict=False) for c in cidrs]


def _in_networks(ip, networks):
    return any(ip in net for net in networks)


def _get_client_ip(request):
    """
    Return the real client IP, walking back through trusted proxy hops.

    When REMOTE_ADDR is a trusted proxy, we inspect X-Forwarded-For
    right-to-left and return the first IP that is not itself a trusted proxy.
    This prevents both XFF spoofing (attacker prepends to the left) and
    WireGuard relay IPs from being treated as the real client.

    If all XFF entries are trusted proxies (e.g. a local container connects
    directly without XFF), we fall back to REMOTE_ADDR itself.
    """
    trusted = _parse_networks(getattr(settings, "TRUSTED_PROXIES", []))

    try:
        remote = ipaddress.ip_address(request.META["REMOTE_ADDR"])
    except (KeyError, ValueError):
        return None

    if not trusted or not _in_networks(remote, trusted):
        return remote

    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    xff_ips = [s.strip() for s in xff.split(",") if s.strip()]

    for ip_str in reversed(xff_ips):
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if not _in_networks(ip, trusted):
            return ip

    # All XFF entries (if any) were trusted proxies — fall back to REMOTE_ADDR.
    return remote


class LocalNetworkOnly(BasePermission):
    message = "Access restricted to local network."

    def has_permission(self, request, view):
        client_ip = _get_client_ip(request)
        if client_ip is None:
            return False
        allowed = _LOOPBACK + _parse_networks(getattr(settings, "API_ALLOWED_IPS", []))
        return _in_networks(client_ip, allowed)
