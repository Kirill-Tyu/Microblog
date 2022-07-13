from sanic_jwt import Responses
from sanic import response

COOKIE_OPTIONS = (
    ("domain", "cookie_domain"),
    ("expires", "cookie_expires"),
    ("max-age", "cookie_max_age"),
    ("samesite", "cookie_samesite"),
    ("secure", "cookie_secure"),
)

def _set_cookie(response, key, value, config, force_httponly=None):
    response.cookies[key] = value
    response.cookies[key]["httponly"] = (
        config.cookie_httponly() if force_httponly is None else force_httponly
    )
    response.cookies[key]["path"] = config.cookie_path()

    for item, option in COOKIE_OPTIONS:
        value = getattr(config, option)()
        if value:
            response.cookies[key][item] = value

class AddRedirectToResponse(Responses):
    def get_token_response(request, *args, **kwargs):
        resp = response.redirect('/users/profile')
        config = kwargs['config']

        if config.cookie_set():
            key = config.cookie_access_token_name()

            if config.cookie_split():
                signature_name = config.cookie_split_signature_name()
                header_payload, signature = args[1].rsplit(
                    ".", maxsplit=1
                )
                _set_cookie(
                    resp, key, header_payload, config, force_httponly=False
                )
                _set_cookie(
                    resp,
                    signature_name,
                    signature,
                    config,
                    force_httponly=True,
                )
            else:
                _set_cookie(resp, key, args[1], config)

            if kwargs['refresh_token'] and config.refresh_token_enabled():
                key = config.cookie_refresh_token_name()
                _set_cookie(resp, key, kwargs['refresh_token'], config)

        return resp