<?php
// Worldpay Hosted Payment Pages Test
if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    header('Content-Type: application/json');
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: POST, OPTIONS, GET');
    header('Access-Control-Allow-Headers: Content-Type');
    exit(0);
}

// Worldpay credentials
$username = 'evQNpTg2ScurKUxK';
$password = 'uIQbwozYFFlClnbfJl3vc3Zn0G5HBvg6KTtZeuXn4DqPa9m67R15Ebrq0uZhUGxm';

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    // Set HTML content type for GET requests
    header('Content-Type: text/html');
    // Show test form
    echo '<!DOCTYPE html>
    <html>
    <head>
        <title>Worldpay Direct Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .test-section { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
            .result { background: #e7f3ff; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .error { background: #ffe7e7; }
            .success { background: #e7ffe7; }
            pre { background: white; padding: 10px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>Worldpay API Direct Test</h1>
        
        <div class="test-section">
            <h2>Test 1: Authorization Endpoint (Direct Payment)</h2>
            <button onclick="testAuthorization()">Test Authorization</button>
            <div id="auth-result" class="result" style="display: none;"></div>
        </div>
        
        <div class="test-section">
            <h2>Test 2: Try Different Hosted Payment Approaches</h2>
            <button onclick="testHostedPayments()">Test Hosted Payments</button>
            <div id="hosted-result" class="result" style="display: none;"></div>
        </div>

        <script>
        async function testAuthorization() {
            const resultDiv = document.getElementById("auth-result");
            resultDiv.style.display = "block";
            resultDiv.innerHTML = "Testing authorization endpoint...";
            
            try {
                const response = await fetch(window.location.href, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ test: "authorization" })
                });
                const result = await response.text();
                resultDiv.innerHTML = "<pre>" + result + "</pre>";
                resultDiv.className = "result success";
            } catch (error) {
                resultDiv.innerHTML = "Error: " + error.message;
                resultDiv.className = "result error";
            }
        }
        
        async function testHostedPayments() {
            const resultDiv = document.getElementById("hosted-result");
            resultDiv.style.display = "block";
            resultDiv.innerHTML = "Testing hosted payment approaches...";
            
            try {
                const response = await fetch(window.location.href, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ test: "hosted" })
                });
                const result = await response.text();
                resultDiv.innerHTML = "<pre>" + result + "</pre>";
                resultDiv.className = "result success";
            } catch (error) {
                resultDiv.innerHTML = "Error: " + error.message;
                resultDiv.className = "result error";
            }
        }
        </script>
    </body>
    </html>';
    exit;
}

// Handle POST requests - set JSON content type for API responses
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS, GET');
header('Access-Control-Allow-Headers: Content-Type');

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data || !isset($data['test'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid request']);
    exit;
}

$auth = base64_encode($username . ':' . $password);

if ($data['test'] === 'authorization') {
    // Test with correct Worldpay Gateway API v6 schema
    $transaction_ref = 'TXN-' . time() . '-' . rand(1000, 9999);
    
    $payload = [
        'transactionReference' => $transaction_ref,
        'merchant' => [
            'entity' => 'PO4080334630'  // Use your actual entity ID
        ],
        'instruction' => [
            'value' => [
                'amount' => 2000,
                'currency' => 'GBP'
            ],
            'narrative' => [
                'line1' => 'Test payment from WAMP'
            ],
            'paymentInstrument' => [
                'type' => 'card/plain',
                'cardNumber' => '4444333322221111',
                'cardExpiryDate' => [  // Fixed: was 'expiryDate', now 'cardExpiryDate'
                    'month' => 12,
                    'year' => 2025
                ],
                'cvc' => '123',
                'cardHolderName' => 'John Smith'
            ]
        ]
    ];
    
    // Also try v5 with correct structure
    $payload_v5 = [
        'transactionReference' => $transaction_ref,
        'merchant' => [
            'entity' => 'PO4080334630'  // Use your actual entity ID
        ],
        'instruction' => [
            'value' => [
                'amount' => 2000,
                'currency' => 'GBP'
            ],
            'narrative' => [
                'line1' => 'Test payment from WAMP'
            ],
            'paymentInstrument' => [
                'type' => 'card/plain',
                'cardNumber' => '4444333322221111',
                'cardExpiryDate' => [
                    'month' => 12,
                    'year' => 2025
                ],
                'cvc' => '123',
                'cardHolderName' => 'John Smith'
            ]
        ]
    ];
    
    $tests = [
        [
            'version' => 'v6',
            'content_type' => 'application/vnd.worldpay.payments-v6+json',
            'payload' => $payload
        ],
        [
            'version' => 'v5',
            'content_type' => 'application/vnd.worldpay.payments-v5+json', 
            'payload' => $payload_v5
        ]
    ];
    
    $results = [];
    
    foreach ($tests as $test) {
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://try.access.worldpay.com/payments/authorizations',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($test['payload']),
            CURLOPT_HTTPHEADER => [
                'Authorization: Basic ' . $auth,
                'Content-Type: ' . $test['content_type'],
                'Accept: ' . $test['content_type']
            ],
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_SSL_VERIFYHOST => false,
        ]);
        
        $response = curl_exec($curl);
        $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        $error = curl_error($curl);
        curl_close($curl);
        
        $results[] = [
            'version' => $test['version'],
            'content_type' => $test['content_type'],
            'http_code' => $http_code,
            'response' => json_decode($response, true),
            'response_raw' => substr($response, 0, 1000),
            'error' => $error,
            'payload_sent' => $test['payload']
        ];
        
        // If we get a successful response, break
        if ($http_code >= 200 && $http_code < 300) {
            break;
        }
    }
    
    echo json_encode([
        'test_type' => 'Worldpay Gateway API v5/v6 Schema Test',
        'endpoint' => 'https://try.access.worldpay.com/payments/authorizations',
        'results' => $results
    ]);
    
} elseif ($data['test'] === 'hosted') {
    // Test different approaches for hosted payments
    $results = [];
    
    // Try 1: Simple redirect approach
    $simple_payload = [
        'amount' => 2000,
        'currency' => 'GBP',
        'orderDescription' => 'Test hosted payment',
        'customerOrderCode' => 'HOSTED-' . time(),
        'successUrl' => 'http://localhost/wamptrial/success.html',
        'failureUrl' => 'http://localhost/wamptrial/failure.html',
        'cancelUrl' => 'http://localhost/wamptrial/index.html'
    ];
    
    $hosted_endpoints = [
        'https://try.access.worldpay.com/payments/redirects',
        'https://try.access.worldpay.com/payments/hosted',
        'https://try.access.worldpay.com/hosted-payments',
        'https://try.access.worldpay.com/checkout',
        'https://try.access.worldpay.com/sessions'
    ];
    
    foreach ($hosted_endpoints as $endpoint) {
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => $endpoint,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($simple_payload),
            CURLOPT_HTTPHEADER => [
                'Authorization: Basic ' . $auth,
                'Content-Type: application/json',
                'Accept: application/json'
            ],
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_SSL_VERIFYHOST => false,
        ]);
        
        $response = curl_exec($curl);
        $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        $error = curl_error($curl);
        curl_close($curl);
        
        $results[] = [
            'endpoint' => $endpoint,
            'http_code' => $http_code,
            'response' => json_decode($response, true),
            'response_raw' => substr($response, 0, 500) . '...',
            'error' => $error
        ];
        
        // If we get a 2xx response, this might be working
        if ($http_code >= 200 && $http_code < 300) {
            break;
        }
    }
    
    echo json_encode([
        'test_type' => 'Hosted Payment Attempts',
        'payload_sent' => $simple_payload,
        'results' => $results
    ]);
}
?>
