from flask import Flask, request, jsonify
import sys
from model import get_recommendations, get_all_users

# Initialize Flask web application
web_app = Flask(__name__)

# Embedded HTML template
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Recommendation System</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Select2 CSS for searchable dropdown -->
    <link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
    <link href="https://cdn.jsdelivr.net/npm/select2-bootstrap-5-theme@1.3.0/dist/select2-bootstrap-5-theme.min.css" rel="stylesheet" />
    
    <!-- Font Awesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px 0;
        }
        
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .card {
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            border: none;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px 15px 0 0;
            text-align: center;
        }
        
        .header h1 {
            margin: 0;
            font-weight: bold;
            font-size: 2.5rem;
        }
        
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .btn-recommend {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 12px 30px;
            font-weight: bold;
            width: 100%;
        }
        
        .btn-recommend:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        
        .btn-reset {
            background: #6c757d;
            border: none;
            padding: 12px 20px;
            font-weight: bold;
        }
        
        .btn-reset:hover {
            background: #5a6268;
        }
        
        .results-section {
            margin-top: 30px;
            display: none;
        }
        
        .table-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .table thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .table thead th {
            border: none;
            padding: 15px;
            font-weight: 600;
        }
        
        .table tbody tr {
            transition: all 0.3s ease;
        }
        
        .table tbody tr:hover {
            background-color: #f8f9fa;
            transform: scale(1.01);
        }
        
        .rating-badge {
            background: #ffc107;
            color: #000;
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: bold;
        }
        
        .positive-badge {
            background: #28a745;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: bold;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        
        .spinner-border {
            width: 3rem;
            height: 3rem;
        }
        
        .select2-container--bootstrap-5 .select2-selection {
            min-height: 48px;
            padding: 8px;
            font-size: 1rem;
        }
        
        .alert-custom {
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
        }
        
        .no-results {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        
        .no-results i {
            font-size: 4rem;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="card">
            <div class="header">
                <h1><i class="fas fa-shopping-bag"></i> Product Recommendation System</h1>
                <p>Sentiment-Based Personalized Recommendations</p>
            </div>
            
            <div class="content">
                <!-- User Selection Section -->
                <div class="row mb-4">
                    <div class="col-md-10">
                        <label for="username-select" class="form-label">
                            <i class="fas fa-user"></i> Select Username
                        </label>
                        <select id="username-select" class="form-select" style="width: 100%;">
                            <option value="">-- Search and select a username --</option>
                        </select>
                    </div>
                    <div class="col-md-2 d-flex align-items-end">
                        <button id="reset-btn" class="btn btn-reset btn-sm w-100">
                            <i class="fas fa-redo"></i> Reset
                        </button>
                    </div>
                </div>
                
                <!-- Recommend Button -->
                <div class="row mb-4">
                    <div class="col-12">
                        <button id="recommend-btn" class="btn btn-primary btn-recommend">
                            <i class="fas fa-magic"></i> Get Recommendations
                        </button>
                    </div>
                </div>
                
                <!-- Loading Spinner -->
                <div class="loading" id="loading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3">Generating personalized recommendations...</p>
                </div>
                
                <!-- Alert Messages -->
                <div id="alert-container"></div>
                
                <!-- Results Section -->
                <div class="results-section" id="results-section">
                    <h3 class="mb-4">
                        <i class="fas fa-star"></i> Top 5 Recommendations for: 
                        <span id="selected-username" class="text-primary"></span>
                    </h3>
                    
                    <div class="table-container">
                        <div class="table-responsive">
                            <table class="table table-hover align-middle" id="results-table">
                                <thead>
                                    <tr>
                                        <th style="width: 5%;">#</th>
                                        <th style="width: 40%;">Product Name</th>
                                        <th style="width: 20%;">Brand</th>
                                        <th style="width: 15%;">Avg Rating</th>
                                        <th style="width: 15%;">Positive %</th>
                                        <th style="width: 10%;">Reviews</th>
                                    </tr>
                                </thead>
                                <tbody id="results-tbody">
                                    <!-- Results will be inserted here -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="text-center mt-4 text-white">
            <p><i class="fas fa-brain"></i> Powered by Machine Learning & Sentiment Analysis</p>
        </div>
    </div>
    
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Select2 JS -->
    <script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
    
    <script>
        $(document).ready(function() {
            // Initialize Select2 for searchable dropdown
            $('#username-select').select2({
                theme: 'bootstrap-5',
                placeholder: '-- Search and select a username --',
                allowClear: true,
                width: '100%'
            });
            
            // Load usernames on page load
            loadUsernames();
            
            // Recommend button click handler
            $('#recommend-btn').click(function() {
                const username = $('#username-select').val();
                
                if (!username) {
                    showAlert('warning', 'Please select a username first!');
                    return;
                }
                
                getRecommendations(username);
            });
            
            // Reset button click handler
            $('#reset-btn').click(function() {
                $('#username-select').val('').trigger('change');
                $('#results-section').hide();
                $('#alert-container').empty();
            });
            
            // Load usernames function
            function loadUsernames() {
                $.ajax({
                    url: '/get_usernames',
                    method: 'GET',
                    success: function(response) {
                        if (response.success) {
                            // Clear existing options except the first one
                            $('#username-select').find('option:not(:first)').remove();
                            
                            // Add usernames to dropdown
                            response.usernames.forEach(function(username) {
                                $('#username-select').append(new Option(username, username));
                            });
                        } else {
                            showAlert('danger', 'Error loading usernames: ' + response.error);
                        }
                    },
                    error: function(xhr, status, error) {
                        showAlert('danger', 'Failed to load usernames. Please refresh the page.');
                    }
                });
            }
            
            // Get recommendations function
            function getRecommendations(username) {
                // Show loading spinner
                $('#loading').show();
                $('#results-section').hide();
                $('#alert-container').empty();
                
                $.ajax({
                    url: '/recommend',
                    method: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ username: username }),
                    success: function(response) {
                        $('#loading').hide();
                        
                        if (response.success && response.recommendations.length > 0) {
                            displayRecommendations(username, response.recommendations);
                        } else {
                            showAlert('info', response.error || 'No recommendations found for this user.');
                        }
                    },
                    error: function(xhr, status, error) {
                        $('#loading').hide();
                        showAlert('danger', 'Failed to get recommendations. Please try again.');
                    }
                });
            }
            
            // Display recommendations function
            function displayRecommendations(username, recommendations) {
                $('#selected-username').text(username);
                $('#results-tbody').empty();
                
                recommendations.forEach(function(rec, index) {
                    const row = `
                        <tr>
                            <td><strong>${index + 1}</strong></td>
                            <td><strong>${rec.product_name}</strong></td>
                            <td>${rec.brand}</td>
                            <td><span class="rating-badge">⭐ ${rec.avg_rating}</span></td>
                            <td><span class="positive-badge">${rec.positive_ratio}%</span></td>
                            <td>${rec.total_reviews}</td>
                        </tr>
                    `;
                    $('#results-tbody').append(row);
                });
                
                $('#results-section').fadeIn();
            }
            
            // Show alert function
            function showAlert(type, message) {
                const alertHtml = `
                    <div class="alert alert-${type} alert-dismissible fade show alert-custom" role="alert">
                        <i class="fas fa-${type === 'danger' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
                        ${message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `;
                $('#alert-container').html(alertHtml);
            }
        });
    </script>
</body>
</html>
"""

class APIResponseHandler: 
    @staticmethod
    def success_response(data_payload):
        return jsonify({
            'success': True,
            **data_payload
        })
    
    @staticmethod
    def error_response(error_details):
        return jsonify({
            'success': False,
            'error': str(error_details)
        })

class UserRepository:
    @staticmethod
    def retrieve_all_usernames():
        try:
            username_collection = get_all_users()
            return username_collection
        except Exception as retrieval_error:
            print(f"Username retrieval failed: {retrieval_error}", file=sys.stderr)
            return []

class RecommendationService:
    @staticmethod
    def generate_for_user(target_username):
        if not target_username or target_username.strip() == '':
            return None, "Username parameter is required"
        
        try:
            print(f"\n{'='*50}")
            print(f"Processing recommendation request")
            print(f"Target User: {target_username}")
            print(f"{'='*50}")
            
            recommendation_results = get_recommendations(target_username)
            
            print(f"Result: Generated {len(recommendation_results)} recommendations")
            print(f"{'='*50}\n")
            
            return recommendation_results, None
        
        except Exception as processing_error:
            error_message = f"Recommendation generation failed: {processing_error}"
            print(error_message, file=sys.stderr)
            import traceback
            traceback.print_exc()
            return None, error_message

# Route handlers
@web_app.route('/')
def serve_homepage():
    return HTML_TEMPLATE

@web_app.route('/get_usernames', methods=['GET'])
def handle_username_request():
    try:
        user_list = UserRepository.retrieve_all_usernames()
        return APIResponseHandler.success_response({'usernames': user_list})
    except Exception as endpoint_error:
        return APIResponseHandler.error_response(endpoint_error)


@web_app.route('/recommend', methods=['POST'])
def handle_recommendation_request():
    try:
        request_payload = request.get_json()
        target_user = request_payload.get('username')
        results, error_msg = RecommendationService.generate_for_user(target_user)
        
        if error_msg:
            return APIResponseHandler.error_response(error_msg)
        
        if not results or len(results) == 0:
            return APIResponseHandler.error_response(
                'No recommendations available for this user'
            )
        
        return APIResponseHandler.success_response({'recommendations': results})
    
    except Exception as endpoint_error:
        print(f"Endpoint error: {endpoint_error}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return APIResponseHandler.error_response(endpoint_error)


def initialize_application():
    try:
        available_users = get_all_users()
    except Exception as init_error:
        print(f"⚠ Warning: Initialization issue - {init_error}", file=sys.stderr)

if __name__ == '__main__':
    initialize_application()
    
    # Launch Flask development server
    web_app.run(
        debug=True,
        port=5000,
        host='127.0.0.1'
    )