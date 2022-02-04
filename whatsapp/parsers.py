def parse_text(message):
    return message["text"]["body"]


def parse_interactive(message):
    return message["interactive"]["list_reply"]["id"]


def parse_button(message):
    return message["interactive"]["button_reply"]["id"]


def parse_contact(message):
    contact = message['contacts'][0]
    return {
        'name': contact['name']['formatted_name'],
        'phone': contact['phones'][0]['wa_id'],
    }


def parse_contacts(message):
    contacts = message['contacts']

    return list(
        map(
            lambda contact: {
                'name': contact['name']['formatted_name'],
                'phone': contact['phones'][0]['wa_id'],
            },
            contacts
        )
    )


def parse_order(message):
    product_items = message['order']["product_items"]
    return product_items


def parse(message, message_type):
    if message_type not in [
        "text",
        "interactive",
        "button",
        "contact",
        "contacts"
    ]:
        raise ValueError(f"Message type {message_type} not supported")
    parser_function = globals()[f"parse_{message_type}"]
    try:
        return parser_function(message)
    except KeyError:
        return False
