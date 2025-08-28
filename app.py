import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from symptom_checker import get_disease_from_symptoms
from DrugInteraction import DrugInteractionChecker, get_ai_drug_interaction
from Personalised_Medication import get_personalized_medication, check_medication_safety
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import overpy
import html

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/symptom-checker', methods=['GET', 'POST'])
def symptom_checker():
    if request.method == 'POST':
        try:
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
                
            symptoms = request.json.get('symptoms')
            if not symptoms:
                return jsonify({'error': 'No symptoms provided'}), 400
                
            result = get_disease_from_symptoms(symptoms)
            if not result:
                return jsonify({'error': 'Failed to analyze symptoms. Please check your API key and try again.'}), 500
                
            return jsonify({'result': result})
            
        except Exception as e:
            print(f"Error in symptom checker: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
            
    return render_template('symptom_checker.html')

@app.route('/drug-interaction', methods=['GET', 'POST'])
def drug_interaction():
    if request.method == 'POST':
        try:
            # Ensure we have JSON data
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
                
            data = request.get_json()
            drug1 = data.get('drug1', '').strip().lower()
            drug2 = data.get('drug2', '').strip().lower()
            
            if not drug1 or not drug2:
                return jsonify({
                    'error': 'Both drug names are required'
                }), 400
            
            result = {
                'database_result': None,
                'ai_result': None
            }
            
            # Get database results if available
            try:
                checker = DrugInteractionChecker()
                db_result = checker.check_interaction(drug1, drug2)
                if db_result:
                    result['database_result'] = db_result
            except Exception as e:
                print(f"Database check error: {str(e)}")
                # Continue even if database check fails
            
            # Get AI analysis
            try:
                ai_result = get_ai_drug_interaction(drug1, drug2)
                if ai_result:
                    result['ai_result'] = ai_result
            except Exception as e:
                print(f"AI analysis error: {str(e)}")
                # Continue even if AI analysis fails
            
            # If both checks failed, return an error
            if not result['database_result'] and not result['ai_result']:
                return jsonify({
                    'error': 'Unable to check interactions at this time. Please try again later.'
                }), 500
                
            return jsonify(result)
            
        except Exception as e:
            print(f"Error in drug interaction check: {str(e)}")
            return jsonify({
                'error': f'An error occurred: {str(e)}'
            }), 500
            
    # Handle GET request - render the form
    return render_template('drug_interaction.html')

@app.route('/personalized-medication', methods=['GET', 'POST'])
def personalized_medication():
    if request.method == 'GET':
        return render_template('personalized_medication.html')
        
    # Handle POST request
    try:
        # Log raw request data
        raw_data = request.get_data()
        print("\n=== Received raw request data ===")
        print(f"Raw data: {raw_data}")
        
        # Parse JSON data
        try:
            data = request.get_json()
            if not data:
                raise ValueError("No JSON data in request")
        except Exception as e:
            print(f"Error parsing JSON: {str(e)}")
            return jsonify({
                'error': 'Invalid request format',
                'details': str(e)
            }), 400
        
        print("\n=== Parsed request data ===")
        print(f"Data type: {type(data)}")
        print(f"Data content: {data}")
        
        # Extract and validate required fields
        condition = data.get('condition', '').strip()
        allergies = data.get('allergies', [])
        current_medications = data.get('current_medications', [])
        
        print("\n=== Extracted data ===")
        print(f"Condition: {condition}")
        print(f"Allergies ({len(allergies)}): {allergies}")
        print(f"Current Medications ({len(current_medications)}): {current_medications}")
        
        if not condition:
            error_msg = 'Medical condition is required'
            print(f"Validation error: {error_msg}")
            return jsonify({
                'error': error_msg,
                'field': 'condition'
            }), 400
            
        # Get personalized medication recommendations
        print("\n=== Calling get_personalized_medication ===")
        try:
            recommendations = get_personalized_medication(
                condition=condition,
                patient_allergies=allergies,
                current_medications=current_medications
            )
            print(f"Recommendations type: {type(recommendations)}")
            print(f"Recommendations content (first 200 chars): {str(recommendations)[:200]}...")
            
            if not recommendations:
                raise ValueError("No recommendations were generated")
                
            # Ensure we have a string response
            if not isinstance(recommendations, str):
                recommendations = str(recommendations)
                
            # Check if the response looks like an error
            if 'error' in recommendations.lower() or 'sorry' in recommendations.lower():
                raise ValueError(f"API returned an error-like response: {recommendations[:200]}...")
                
            return jsonify({
                'recommendations': recommendations,
                'status': 'success'
            })
            
        except Exception as e:
            print(f"Error in get_personalized_medication: {str(e)}")
            return jsonify({
                'error': 'Failed to generate recommendations',
                'details': str(e),
                'recommendations': 'We encountered an issue generating recommendations. Please try again or consult with a healthcare provider.'
            }), 500
        
        # Check for potential interactions if we have current medications
        interactions = {}
        if current_medications:
            # Extract medication names from the recommendations text (simple approach)
            # In a production app, you'd want to parse this more robustly
            recommended_meds = []
            for line in recommendations.split('\n'):
                if line.strip().startswith('- '):
                    med = line.strip().split(':')[0].replace('-', '').strip()
                    if med and med.lower() not in ['no specific recommendations', 'no known allergies']:
                        recommended_meds.append(med)
            
            if recommended_meds:
                interactions = check_medication_safety(
                    recommended_meds=recommended_meds,
                    current_meds=current_medications
                )
        
        return jsonify({
            'recommendations': recommendations.get('recommendations', 'No specific recommendations available.'),
            'interactions': interactions,
            'recommended_medications': recommendations.get('recommended_medications', [])
        })
        
    except Exception as e:
        print(f"Error in personalized medication: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/hospital-locator')
def hospital_locator():
    # Get the Mapbox token from environment variables
    mapbox_token = os.getenv('MAPBOX_ACCESS_TOKEN')
    print(f"Mapbox token: {'Found' if mapbox_token else 'Not found'}")
    if not mapbox_token:
        print("Warning: MAPBOX_ACCESS_TOKEN environment variable is not set")
    # Pass the Mapbox token to the template
    return render_template('hospital_locator.html', mapbox_token=mapbox_token)

@app.route('/hospital-locator', methods=['POST'])
def find_hospitals():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'})
        
        print(f"Received request data: {data}")
        
        address = data.get('address')
        if not address:
            return jsonify({'error': 'Please provide an address'})
            
        radius = int(data.get('radius', 5000))
        if radius < 1000 or radius > 10000:
            radius = 5000

        print(f"Searching for: {address} with radius {radius}m")

        try:
            # Initialize geocoder with a longer timeout and user agent
            geolocator = Nominatim(
                user_agent="chiron_healthcare_assistant",
                timeout=10
            )
            
            # Get user's location with more specific parameters
            location = geolocator.geocode(
                address,
                exactly_one=True,
                language="en",
                country_codes="in"  # Limit to India
            )
            
            if not location:
                return jsonify({'error': 'Could not find the specified location. Please try a more specific address in India.'})
            
            print(f"Found location: {location.address} at {location.latitude}, {location.longitude}")
            
            user_location = (location.latitude, location.longitude)
        except Exception as e:
            print(f"Geocoding error: {str(e)}")
            return jsonify({'error': 'Failed to find the location. Please try a more specific address.'})
        
        try:
            # Get medical facilities using a simpler query
            api = overpy.Overpass()
            
            # Split the query into two parts to avoid timeout
            # First query: Hospitals
            hospital_query = f"""
            [out:json][timeout:25];
            (
              node["amenity"="hospital"](around:{radius},{user_location[0]},{user_location[1]});
              way["amenity"="hospital"](around:{radius},{user_location[0]},{user_location[1]});
            );
            out body;
            >;
            out skel qt;
            """
            
            # Second query: Pharmacies
            pharmacy_query = f"""
            [out:json][timeout:25];
            (
              node["amenity"="pharmacy"](around:{radius},{user_location[0]},{user_location[1]});
              way["amenity"="pharmacy"](around:{radius},{user_location[0]},{user_location[1]});
            );
            out body;
            >;
            out skel qt;
            """
            
            print("Querying hospitals...")
            hospital_result = api.query(hospital_query)
            print(f"Found {len(hospital_result.nodes)} hospital nodes and {len(hospital_result.ways)} hospital ways")
            
            print("Querying pharmacies...")
            pharmacy_result = api.query(pharmacy_query)
            print(f"Found {len(pharmacy_result.nodes)} pharmacy nodes and {len(pharmacy_result.ways)} pharmacy ways")
            
            facilities = []
            hospitals_count = 0
            pharmacies_count = 0
            
            # Process hospital nodes
            for node in hospital_result.nodes:
                name = node.tags.get('name', 'Hospital')
                facility_coords = (node.lat, node.lon)
                distance = round(geodesic(user_location, facility_coords).kilometers, 2)
                
                details = {
                    'phone': node.tags.get('phone', 'Not available'),
                    'emergency': node.tags.get('emergency', 'Unknown'),
                    'healthcare': node.tags.get('healthcare', 'General'),
                    'opening_hours': node.tags.get('opening_hours', 'Not specified'),
                    'website': node.tags.get('website', ''),
                    'wheelchair': node.tags.get('wheelchair', 'Unknown'),
                    'address': node.tags.get('addr:full', node.tags.get('addr:street', 'Address not available'))
                }
                
                facility = {
                    'type': 'hospital',
                    'name': html.escape(name),
                    'lat': float(node.lat),
                    'lon': float(node.lon),
                    'distance': distance,
                    'details': details,
                    'directions_url': f"https://www.google.com/maps/dir/?api=1&origin={user_location[0]},{user_location[1]}&destination={node.lat},{node.lon}&travelmode=driving"
                }
                facilities.append(facility)
                hospitals_count += 1
            
            # Process pharmacy nodes
            for node in pharmacy_result.nodes:
                name = node.tags.get('name', 'Pharmacy')
                facility_coords = (node.lat, node.lon)
                distance = round(geodesic(user_location, facility_coords).kilometers, 2)
                
                details = {
                    'phone': node.tags.get('phone', 'Not available'),
                    'opening_hours': node.tags.get('opening_hours', 'Not specified'),
                    'website': node.tags.get('website', ''),
                    'wheelchair': node.tags.get('wheelchair', 'Unknown'),
                    'address': node.tags.get('addr:full', node.tags.get('addr:street', 'Address not available'))
                }
                
                facility = {
                    'type': 'pharmacy',
                    'name': html.escape(name),
                    'lat': float(node.lat),
                    'lon': float(node.lon),
                    'distance': distance,
                    'details': details,
                    'directions_url': f"https://www.google.com/maps/dir/?api=1&origin={user_location[0]},{user_location[1]}&destination={node.lat},{node.lon}&travelmode=driving"
                }
                facilities.append(facility)
                pharmacies_count += 1
            
            # Sort facilities by distance
            facilities.sort(key=lambda x: x['distance'])
            
            response_data = {
                'user_location': {
                    'lat': float(user_location[0]),
                    'lon': float(user_location[1]),
                    'address': location.address
                },
                'facilities': facilities,
                'stats': {
                    'hospitals': hospitals_count,
                    'pharmacies': pharmacies_count
                }
            }
            
            print(f"Found {hospitals_count} hospitals and {pharmacies_count} pharmacies")
            return jsonify(response_data)
            
        except overpy.exception.OverpassTooManyRequests:
            print("Overpass API rate limit exceeded")
            return jsonify({'error': 'Too many requests. Please try again later.'})
        except overpy.exception.OverpassGatewayTimeout:
            print("Overpass API timeout")
            return jsonify({'error': 'The search took too long. Please try with a smaller radius.'})
        except Exception as e:
            print(f"Overpass API error: {str(e)}")
            return jsonify({'error': 'Failed to fetch medical facilities. Please try again.'})
            
    except ValueError as e:
        print(f"ValueError: {str(e)}")
        return jsonify({'error': f'Invalid input: {str(e)}'})
    except Exception as e:
        print(f"Error in find_hospitals: {str(e)}")
        return jsonify({'error': 'An error occurred while searching for medical facilities. Please try again.'})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render provides PORT environment variable
    app.run(host="0.0.0.0", port=port, debug=True)
