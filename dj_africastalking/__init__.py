# import package
from django.conf import settings
import africastalking

# Initialize SDK
username = settings.AFRICASTALKING['username']    # use 'sandbox' for development in the test environment
api_key = settings.AFRICASTALKING['api_key']      # use your sandbox app API key for development in the test environment
africastalking.initialize(username, api_key)
