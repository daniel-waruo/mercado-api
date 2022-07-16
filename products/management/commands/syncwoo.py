from django.core.management.base import BaseCommand

from services.shop.utils import update_facebook_batch_from_woo


class Command(BaseCommand):
    help = 'Adds woocommerce products to facebook'

    def handle(self, *args, **options):
        update_facebook_batch_from_woo()
        self.stdout.write(self.style.SUCCESS('Successfully uploaded products'))
