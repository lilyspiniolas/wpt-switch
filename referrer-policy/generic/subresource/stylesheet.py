import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import subresource

def generate_payload(request, server_data):
    data = ('{"headers": %(headers)s}') % server_data
    type = 'image'
    if "type" in request.GET:
        type = request.GET["type"]

    if "id" in request.GET:
        request.server.stash.put(request.GET["id"], data)

    if type == 'image':
        return subresource.get_template("image.css.template") % {"id": request.GET["id"]}

    elif type == 'svg':
        return subresource.get_template("svg.css.template") % {
            "id": request.GET["id"],
            "property": request.GET["property"]}

def generate_import_rule(request, server_data):
    type = 'image'
    property = None;
    if "type" in request.GET:
        type = request.GET["type"]
    if type == "svg" and "property" in request.GET:
        property = request.GET["property"]
    if property is None:
        return "@import url('%(url)s?id=%(id)s&type=%(type)s');" % {
            "id": request.GET["id"],
            "url": subresource.create_redirect_url(request, cross_origin = True),
            "type": type
        }
    return "@import url('%(url)s?id=%(id)s&type=%(type)s&property=%(property)s');" % {
        "id": request.GET["id"],
        "url": subresource.create_redirect_url(request, cross_origin = True),
        "type": type,
        "property": property
    }

def main(request, response):
    payload_generator = lambda data: generate_payload(request, data)
    content_type = "text/css"
    referrer_policy = "unsafe-url"
    if "import-rule" in request.GET:
        payload_generator = lambda data: generate_import_rule(request, data)

    if "report-headers" in request.GET:
        payload_generator = lambda data: generate_report_headers_payload(request, data)
        content_type = 'application/json'

    if "referrer-policy" in request.GET:
        referrer_policy = request.GET["referrer-policy"]

    subresource.respond(
        request,
        response,
        payload_generator = payload_generator,
        content_type = content_type,
        maybe_additional_headers = { "Referrer-Policy": referrer_policy })

