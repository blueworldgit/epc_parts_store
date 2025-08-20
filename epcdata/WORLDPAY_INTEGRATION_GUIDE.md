# Worldpay Hosted Payment Pages Integration

This documentation explains how to set up and configure Worldpay Hosted Payment Pages for your Django Oscar e-commerce site.

## Overview

The integration uses Worldpay's modern Hosted Payment Pages API, which provides:
- Secure card processing without handling sensitive data
- PCI DSS compliance
- Modern payment experience
- Support for multiple payment methods
- Mobile-responsive payment pages

## Files Updated/Created

### New Files
- `payment/facade.py` - API communication with Worldpay
- `payment/views.py` - Payment flow views  
- `payment/forms.py` - Payment method selection form
- `templates/payment/worldpay_success.html` - Success page
- `templates/payment/worldpay_failure.html` - Failure page
- `templates/payment/worldpay_cancel.html` - Cancel page

### Modified Files
- `checkout/views.py` - Custom payment details view
- `templates/oscar/checkout/payment_details.html` - Updated payment form
- `epcdata/settings.py` - Added Worldpay configuration
- `requirements.txt` - Added requests library

## Configuration

### 1. Environment Variables

Add these to your `.env` file:

```bash
# Worldpay API Configuration
WORLDPAY_USERNAME=your_username_here
WORLDPAY_PASSWORD=your_password_here
WORLDPAY_ENTITY_ID=your_entity_id_here
WORLDPAY_TEST_MODE=True
```

### 2. Get Worldpay Credentials

1. Log in to your Worldpay Access Portal/Dashboard
2. Navigate to "Developer Tools" or "API Credentials"  
3. Generate/find your **username and password** (NOT service key)
4. Find your **Entity ID** in the dashboard under "Developer Tools"

**Important**: Worldpay Hosted Payment Pages uses **Basic Authentication** (username:password), not Bearer tokens.

### 3. Test Credentials

For testing purposes, you can use test credentials provided by Worldpay in their documentation.

## How It Works

### Payment Flow

1. **Customer selects payment method** - On the payment details page
2. **Customer clicks "Proceed to Payment"** - Redirects to Worldpay redirect view
3. **API call creates payment session** - Server calls Worldpay API with order details
4. **Customer redirected to Worldpay** - Secure hosted payment page
5. **Customer enters card details** - On Worldpay's secure servers
6. **Payment processed** - Worldpay handles the transaction
7. **Customer redirected back** - To success, failure, or cancel page
8. **Order completed** - Payment recorded in Django Oscar

### Technical Details

- **API Integration**: Uses POST requests to Worldpay's payment-pages endpoint
- **Session Management**: Transaction references stored in Django sessions
- **Order Creation**: Orders created before payment to ensure consistency
- **Payment Recording**: Payment sources and transactions recorded on successful payment

## Security Features

- **No card data handling**: All sensitive data processed by Worldpay
- **HTTPS not required for development**: Hosted pages handle security
- **Signed transactions**: Transaction references prevent tampering
- **Session validation**: Callbacks validated against session data

## Testing

### Test Cards

Use Worldpay's test card numbers:
- **Visa**: 4444333322221111
- **Mastercard**: 5555444433221111
- **Expiry**: Any future date
- **CVV**: Any 3 digits

### Test Mode

Ensure `WORLDPAY_TEST_MODE=True` in your environment variables for testing.

## Production Setup

1. Set `WORLDPAY_TEST_MODE=False`
2. Use production Service Key and Entity ID
3. Test thoroughly with real payment methods
4. Monitor payment logs and error handling

## Error Handling

The integration includes comprehensive error handling:
- **API failures**: Logged and user-friendly error messages
- **Network issues**: Timeout and retry logic
- **Invalid responses**: Proper error handling and fallbacks
- **Session validation**: Prevents invalid payment callbacks

## Logging

Payment activities are logged at appropriate levels:
- **INFO**: Normal payment flow events
- **DEBUG**: Detailed API request/response data (test mode only)
- **WARNING**: Recoverable issues
- **ERROR**: Payment failures and critical issues

## Support

For issues with the integration:
1. Check Django logs for detailed error messages
2. Verify Worldpay credentials and configuration
3. Test with Worldpay's test environment first
4. Contact Worldpay support for payment gateway issues

## API Reference

For full Worldpay API documentation, visit:
https://developer.worldpay.com/products/access/hosted-payment-pages
