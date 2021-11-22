from django.template.loader import render_to_string
from orders.models import Order
from screens.screens import Screen as BaseScreen
from products.models import Brand, Product
from screens.utils import get_screen


class Screen(BaseScreen):
    type = 'CON'

    def render_ussd(self):
        return f"{self.type} {self.render()}"


class GetLastOrderScreen(Screen):
    state = 'last_order'
    required_fields = ['product_id']

    def render(self):
        """ asks user whether user wants to use last order """
        response = render_to_string(
            'gas/last_order.txt',
            context={
                **self.context,
                'product': self.context['product']
            }
        )
        return response

    def next_screen(self, current_input: int):
        if current_input not in [1, 2]:
            return self.error_screen(errors=["Invalid Input.Try again"])
        if current_input == 1:
            # this is the yes option
            # if the user wants to use the sam order take them to the order confirmation page
            return get_screen(
                'choose_confirmation_status',
                data={
                    'product_id': self.data['product_id'],
                }
            )
        # If the answer is 2 for no start the Gas Order Flow
        return get_screen('choose_cylinder')


class ChooseProviderScreen(Screen):
    state = 'choose_provider'
    type = 'CON'

    def render(self):
        """function returns a choose provider screen"""
        # query providers and return them ordered by their id
        providers = Brand.objects.all()
        response = render_to_string(
            'gas/choose_provider.txt',
            context={
                'errors': self.errors,
                'providers': providers
            }
        )
        return response

    def next_screen(self, current_input: int):
        try:
            brand = Brand.objects.get_by_position(current_input)
        except Brand.DoesNotExist:
            return self.error_screen(errors=['Invalid option.Check and try again'])
        return get_screen('choose_cylinder', data={
            'provider_id': brand.id
        })


class ChooseCylinderScreen(Screen):
    state = 'choose_cylinder'
    type = 'CON'


    def render(self):
        """return choose gas menu screen"""
        products = Product.objects.filter(sku__startswith='gas')
        # choose products under brand and send it to the template
        response = render_to_string(
            'gas/choose_cylinder.txt',
            context={
                **self.context,
                'errors': self.errors,
                'products': products,
            }
        )
        return response

    def next_screen(self, current_input: int):
        """shows ownership status of the screen"""
        # check for errors in ownership and go to the next step
        # which is ownership status
        try:
            product = Product.objects.get_by_position(
                current_input,
                queryset=Product.objects.filter(sku__startswith='gas')
            )
        except (Product.DoesNotExist, IndexError):
            return self.error_screen(errors=['Invalid option.Check and try again'])
        return get_screen('ownership_status', data={
            'product_id': product.id
        })


class ChooseOwnershipStatusScreen(Screen):
    required_fields = ['product_id']
    state = 'ownership_status'
    type = 'CON'

    def render(self):
        """ return a choose ownership screen"""
        product = Product.objects.get(
            id=self.data['product_id']
        )
        return render_to_string(
            'gas/ownership_status.txt',
            context={
                'errors': self.errors,
                'product': product
            }
        )

    def next_screen(self, current_input):
        if current_input not in [1, 2]:
            return self.error_screen(errors=["Invalid Input.Try again"])
        if current_input == 1:
            return get_screen(
                'choose_confirmation_status',
                data={
                    'product_id': self.data['product_id'],
                    'complementary': False
                }
            )
        if current_input == 2:
            return get_screen('finish_no_cylinder')


class FinishNoCylinderScreen(Screen):
    type = 'END'
    state = 'finish_no_cylinder'

    def render(self):
        """ returns a success message showing the user that we will contact him"""
        # finish no cylinder
        return render_to_string(
            'gas/finish_no_cylinder.txt',
            context={
                'errors': self.errors
            }
        )


class ChooseConfirmationStatusScreen(Screen):
    required_fields = ['product_id']
    state = 'choose_confirmation_status'
    context = None
    type = 'CON'

    def render(self):
        """ returns a confirmation status screen if ownership else finished  """
        # check if the user has valid input
        product = Product.objects.get(
            id=self.data['product_id']
        )
        return render_to_string(
            'gas/confirmation_status.txt',
            context={
                'errors': self.errors,
                'product': product
            }
        )

    def next_screen(self, current_input):
        if current_input not in [1, 2]:
            return self.error_screen(errors=["Invalid Input"])
        if current_input == 1:
            return get_screen(
                'finish_order',
                data={
                    'product_id': self.data['product_id'],
                }
            )
        if current_input == 2:
            return get_screen('choose_cylinder')


class FinishOrderScreen(Screen):
    required_fields = ['product_id']
    state = 'finish_order'
    type = 'END'

    def render(self):
        product = Product.objects.get(
            id=self.data['product_id']
        )
        # make an order
        Order.objects.make_order(
            buyer=self.context['buyer'],
            item=product
        )
        return render_to_string(
            'gas/finish_order.txt',
            context={
                'errors': self.errors,
                'product': product
            }
        )

