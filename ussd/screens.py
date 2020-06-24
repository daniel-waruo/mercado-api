from django.template.loader import render_to_string
from ussd_screens.screens import Screen
from items.models import Brand, Category, Item
from ussd_screens.utils import get_screen


# TODO: validate
class ChooseProviderScreen(Screen):
    state = 'choose_provider'

    def render(self):
        """function returns a choose provider screen"""
        # query providers and return them ordered by their id
        providers = Brand.objects.all()
        response = render_to_string(
            'ussd/choose_provider.txt',
            context={
                'errors': self.errors,
                'providers': providers
            }
        )
        return response

    def next_screen(self, current_input: int):
        try:
            brand = Brand.objects.get_by_position(current_input)
        except Exception:
            return self.error_screen(errors=['Invalid option.Check and try again'])
        return get_screen('choose_cylinder', data={
            'provider_id': brand.id
        })


class ChooseCylinderScreen(Screen):
    required_fields = ['provider_id']
    state = 'choose_cylinder'

    def render(self):
        """return choose gas menu screen"""
        provider = Brand.objects.get(
            id=self.data['provider_id']
        )
        # choose items under brand and send it to the template
        response = render_to_string(
            'ussd/choose_size.txt',
            context={
                'errors': self.errors,
                'provider': provider,
                'items': provider.items.all()
            }
        )
        return response

    def next_screen(self, current_input: int):
        """shows ownership status of the screen"""
        # check for errors in ownership and go to the next step
        # which is ownership status
        try:
            provider = Brand.objects.get(
                id=self.data['provider_id']
            )
            item = Item.objects.get_by_position(
                current_input,
                queryset=provider.items.all()
            )
        except Exception:
            return self.error_screen(errors=['Invalid option.Check and try again'])
        return get_screen('ownership_status', data={
            'provider_id': provider.id,
            'item_id': item.id
        })


class ChooseOwnershipStatusScreen(Screen):
    required_fields = ['provider_id', 'item_id']
    state = 'ownership_status'

    def render(self):
        """ return a choose ownership screen"""
        # else return ownership status menu
        provider = Brand.objects.get(
            id=self.data['provider_id']
        )
        item = Item.objects.get(
            id=self.data['item_id']
        )
        return render_to_string(
            'ussd/ownership_status.txt',
            context={
                'errors': self.errors,
                'provider': provider,
                'item': item
            }
        )

    def next_screen(self, current_input):
        if current_input not in [1, 2]:
            return self.error_screen(errors=["Invalid Input.Try again"])
        if current_input == 1:
            return get_screen(
                'choose_confirmation_status',
                data={
                    'provider_id': self.data['provider_id'],
                    'item_id': self.data['item_id'],
                }
            )
        if current_input == 2:
            return get_screen('finish_no_cylinder')


class FinishNoCylinderScreen(Screen):
    type = 'END'
    state = 'finish_no_cylinder'

    def render(self):
        """returns a success message showing the user that we will contact him"""
        # TODO: add user to no cylinder contact queue
        return render_to_string(
            'ussd/finish_no_cylinder.txt',
            context={
                'errors': self.errors
            }
        )


class ChooseConfirmationStatusScreen(Screen):
    required_fields = ['provider_id', 'item_id']
    state = 'choose_confirmation_status'

    def render(self):
        """ returns a confirmation status screen if ownership else finished  """
        # check if the user has valid input
        provider = Brand.objects.get(
            id=self.data['provider_id']
        )
        item = Item.objects.get(
            id=self.data['item_id']
        )
        return render_to_string(
            'ussd/confirmation_status.txt',
            context={
                'errors': self.errors,
                'provider': provider,
                'item': item
            }
        )

    def next_screen(self, current_input):
        if current_input not in [1, 2]:
            return self.error_screen(errors=["Invalid Input"])
        if current_input == 1:
            return get_screen(
                'finish_order',
                data={
                    ''
                }
            )
        if current_input == 2:
            return get_screen('choose_cylinder')


class FinishOrderScreen(Screen):
    # required_fields = ['provider_id', 'item_id', 'buyer']
    state = 'finish_order'
    type = 'END'

    def render(self):
        """ finished the order or re-initializes it """
        # get buyer
        # call order_gas on buyer
        # call buyer to get delivery information on first
        # send signal order_gas signal
        return render_to_string(
            'ussd/finish_order.txt',
        )
