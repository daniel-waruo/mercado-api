from django.template.loader import render_to_string

from orders.models import Order
from ussd_screens.screens import Screen
from items.models import Brand, Category, Item, ComplementaryItem
from ussd_screens.utils import get_screen
from buyers.models import ContactQueue


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
            'item_id': item.id
        })


class ChooseOwnershipStatusScreen(Screen):
    required_fields = ['item_id']
    state = 'ownership_status'

    def render(self):
        """ return a choose ownership screen"""
        item = Item.objects.get(
            id=self.data['item_id']
        )
        return render_to_string(
            'ussd/ownership_status.txt',
            context={
                'errors': self.errors,
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
                    'item_id': self.data['item_id'],
                    'complementary': False
                }
            )
        if current_input == 2:
            # return get_screen('finish_no_cylinder')
            return get_screen(
                'choose_cylinder_package',
                data={
                    'item_id': self.data['item_id'],
                }
            )


class ChooseCylinderPackage(Screen):
    required_fields = ['item_id']
    state = 'choose_cylinder_package'

    def render(self):
        """ return a choose cylinder package screen"""
        item = Item.objects.get(
            id=self.data['item_id']
        )
        cylinder_packages = item.complementary_items.all()
        return render_to_string(
            'ussd/choose_cylinder_package.txt',
            context={
                'errors': self.errors,
                'packages': cylinder_packages
            }
        )

    def next_screen(self, current_input):
        """get sender option or talk to us request """
        if current_input == 0:
            return get_screen('finish_no_cylinder')

        try:
            item = Item.objects.get(
                id=self.data['item_id']
            )
            complementary_item = item.complementary_items.get_by_position(current_input)
        except Exception:
            return self.error_screen(errors=['Invalid option.Check and try again'])
        return get_screen(
            'choose_confirmation_status',
            data={
                'item_id': complementary_item.id,
                'complementary': True
            }
        )


class FinishNoCylinderScreen(Screen):
    type = 'END'
    state = 'finish_no_cylinder'

    def render(self):
        """returns a success message showing the user that we will contact him"""
        ContactQueue.objects.add(
            buyer=self.context['buyer'],
            reason="NO GAS CYLINDER"
        )
        return render_to_string(
            'ussd/finish_no_cylinder.txt',
            context={
                'errors': self.errors
            }
        )


class ChooseConfirmationStatusScreen(Screen):
    required_fields = ['item_id', 'complementary']
    state = 'choose_confirmation_status'
    context = None

    def render(self):
        """ returns a confirmation status screen if ownership else finished  """
        # check if the user has valid input

        if self.data['complementary']:
            item = ComplementaryItem.objects.get(
                id=self.data['item_id']
            )
        else:
            item = Item.objects.get(
                id=self.data['item_id']
            )
        return render_to_string(
            'ussd/confirmation_status.txt',
            context={
                'errors': self.errors,
                'item': item
            }
        )

    def next_screen(self, current_input):
        if current_input not in [1, 2]:
            return self.error_screen(errors=["Invalid Input"])
        if current_input == 1:
            return get_screen(
                'choose_payment_method',
                data={
                    'item_id': self.data['item_id'],
                    'complementary': self.data['complementary']
                }
            )
        if current_input == 2:
            return get_screen('choose_provider')


class ChoosePaymentMethodScreen(Screen):
    required_fields = ['item_id', 'complementary']
    state = 'choose_payment_method'

    def render(self):
        return render_to_string(
            'ussd/payment_method.txt',
        )

    def next_screen(self, current_input):
        if current_input not in [1, 2]:
            return self.error_screen(errors=["Invalid Input"])
        if current_input == 1:
            return get_screen(
                'finish_mpesa',
                data={
                    'item_id': self.data['item_id'],
                    'complementary': self.data['complementary']
                }
            )
        if current_input == 2:
            return get_screen(
                'finish_order',
                data={
                    'item_id': self.data['item_id'],
                    'complementary': self.data['complementary']
                }
            )


class FinishMpesaPaymentScreen(Screen):
    required_fields = ['item_id', 'complementary']
    state = 'finish_mpesa'
    type = 'END'

    def render(self):
        if self.data['complementary']:
            item = ComplementaryItem.objects.get(
                id=self.data['item_id']
            )
        else:
            item = Item.objects.get(
                id=self.data['item_id']
            )
        # make an order
        order = Order.objects.make_order(
            buyer=self.context['buyer'],
            item=item,
            payment_method='m-pesa'
        )
        order.pay_for_order()
        return render_to_string(
            'ussd/finish_mpesa.txt'
        )


class FinishOrderScreen(Screen):
    required_fields = ['item_id', 'complementary']
    state = 'finish_order'
    type = 'END'

    def render(self):
        if self.data['complementary']:
            item = ComplementaryItem.objects.get(
                id=self.data['item_id']
            )
        else:
            item = Item.objects.get(
                id=self.data['item_id']
            )
        # make an order
        Order.objects.make_order(
            buyer=self.context['buyer'],
            item=item
        )
        return render_to_string(
            'ussd/finish_order.txt',
        )
