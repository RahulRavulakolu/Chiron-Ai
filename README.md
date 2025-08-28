 HEAD
# Chiron-Ai

# Chiron Healthcare Assistant

A comprehensive healthcare assistant application that provides multiple healthcare-related services including hospital location, symptom checking, drug interaction analysis, and personalized medication management.

## Features

### 🏥 Hospital Locator 
- Interactive map interface for locating nearby medical facilities
- Real-time distance calculation from your location
- Detailed facility information including:
  - Contact details and address
  - Operating hours
  - Emergency services availability
  - Accessibility features
  - Direct navigation links
  - Website and contact information

### 🤒 Symptom Checker 
- AI-powered symptom analysis
- Potential condition assessment
- Recommended next steps
- User-friendly interface for symptom input

### 💊 Drug Interaction Checker 
- Comprehensive drug interaction analysis
- Severity indicators for potential interactions
- Detailed interaction explanations
- Alternative medication suggestions

### 💊 Personalized Medication Management 
- Medication tracking and reminders
- Dosage schedule management
- Safety information and guidelines
- Personalized medication recommendations

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- API keys for required services (Mapbox, etc.)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Chiron2.git
cd Chiron2
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your API keys:
     ```
     MAPBOX_ACCESS_TOKEN=your_mapbox_token_here
     ```

## 🏃‍♂️ Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## 🛠️ Project Structure

```
Chiron2/
├── static/             # Static files (CSS, JS, images)
│   └── styles.css      # Main stylesheet
├── templates/          # HTML templates
│   ├── index.html      # Home page
│   ├── hospital_locator.html
│   ├── symptom_checker.html
│   ├── drug_interaction.html
│   └── personalized_medication.html
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Dependencies
- Flask >= 2.0.1: Web framework
- Groq >= 0.18.0: AI model integration
- Geopy >= 2.3.0: Geocoding and distance calculations
- Overpy >= 0.6: OpenStreetMap data access
- Folium >= 0.12.1: Interactive maps
- Additional dependencies listed in `requirements.txt`

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

3. Use the navigation menu to access different features:
   - Hospital Locator: Find nearby medical facilities
   - Symptom Checker: Check your symptoms
   - Drug Interaction: Check medication interactions
   - Personalized Medication: Manage your medications

## Features in Detail

### Hospital Locator
- Enter your location and desired search radius
- View hospitals and pharmacies on an interactive map
- Click markers for detailed facility information
- Get directions to any facility
- Filter by facility type (hospital/pharmacy)

### Symptom Checker
- Enter your symptoms using natural language
- Get AI-powered analysis of potential conditions
- Receive recommendations for medical attention
- View severity levels and urgency

### Drug Interaction
- Enter two or more medications
- View potential interactions from medical database
- Get AI-enhanced analysis of interactions
- See recommendations for safe medication use

### Personalized Medication
- Add your current medications
- Set up dosage schedules
- Receive safety alerts
- Track medication history

## Security and Privacy

- No personal medical data is stored permanently
- All API communications are encrypted
- User location data is used only for immediate searches
- No tracking or analytics implemented

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenStreetMap for medical facility data
- Groq for AI capabilities
- Flask community for web framework
- All contributors and users
 826e9d5 (new updates)
