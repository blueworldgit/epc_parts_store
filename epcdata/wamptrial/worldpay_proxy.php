<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight OPTIONS request
if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    exit(0);
}

// Only allow POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Get the JSON payload
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON payload']);
    exit;
}

// Worldpay credentials
$username = 'evQNpTg2ScurKUxK';
$password = 'uIQbwozYFFlClnbfJl3vc3Zn0G5HBvg6KTtZeuXn4DqPa9m67R15Ebrq0uZhUGxm';

// Based on discovery, test the authorization endpoints
$endpoints = [
    'https://try.access.worldpay.com/payments/authorizations',
    'https://try.access.worldpay.com/payments',
    'https://try.access.worldpay.com/sessions',
    'https://try.access.worldpay.com/payment-sessions',
    'https://try.access.worldpay.com/hosted-payments'
];

$content_types = [
    'application/json',
    'application/vnd.worldpay.payment_pages-v1.hal+json'
];

// Try both POST and GET methods
$methods = ['POST', 'GET'];

$results = [];

foreach ($endpoints as $endpoint) {
    foreach ($content_types as $content_type) {
        foreach ($methods as $method) {
            $curl = curl_init();
            
            $auth = base64_encode($username . ':' . $password);
            
            $headers = [
                'Authorization: Basic ' . $auth,
                'Content-Type: ' . $content_type,
                'Accept: ' . $content_type  // Match Accept header to Content-Type
            ];
            
            $curl_options = [
                CURLOPT_URL => $endpoint,
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_ENCODING => '',
                CURLOPT_MAXREDIRS => 10,
                CURLOPT_TIMEOUT => 30,
                CURLOPT_FOLLOWLOCATION => true,
                CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
                CURLOPT_CUSTOMREQUEST => $method,
                CURLOPT_HTTPHEADER => $headers,
                // Disable SSL verification for testing (DO NOT USE IN PRODUCTION)
                CURLOPT_SSL_VERIFYPEER => false,
                CURLOPT_SSL_VERIFYHOST => false,
            ];
            
            // Only add POST data for POST requests
            if ($method === 'POST') {
                $curl_options[CURLOPT_POSTFIELDS] = json_encode($data['payload']);
            }
            
            curl_setopt_array($curl, $curl_options);
        
        $response = curl_exec($curl);
        $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        $error = curl_error($curl);
        
        curl_close($curl);
        
        $result = [
            'endpoint' => $endpoint,
            'method' => $method,
            'content_type' => $content_type,
            'http_code' => $http_code,
            'success' => ($http_code >= 200 && $http_code < 300),
            'response' => $response ? json_decode($response, true) : null,
            'response_raw' => $response,
            'error' => $error,
            'timestamp' => date('Y-m-d H:i:s'),
            'auth_header' => 'Basic ' . substr($auth, 0, 20) . '...' // Show partial auth for debugging
        ];
        
        $results[] = $result;
        
        // If we found a successful response, return it immediately
        if ($result['success']) {
            echo json_encode([
                'success' => true,
                'working_endpoint' => $endpoint,
                'working_method' => $method,
                'working_content_type' => $content_type,
                'response' => $result['response'],
                'all_results' => $results
            ]);
            exit;
        }
    }
}
}

// If no successful endpoint found, return all results for debugging
echo json_encode([
    'success' => false,
    'message' => 'No working endpoint found',
    'all_results' => $results
]);
?>
