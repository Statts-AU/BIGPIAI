# BIGPIAI - AI-Powered Document Processing Platform

BIGPIAI is a comprehensive AI-powered platform for document processing, CV analysis, and template generation. The platform offers multiple phases of document processing capabilities, from basic analysis to advanced template-based generation.

## Features

### Phase 1: AI-Powered Writing Plan Generation
- Structured writing plan creation from documents
- Smart key point extraction using NLP
- Customizable templates for different document types
- Excel format output for easy editing

### Phase 2: Advanced AI Template & Content Generation
- Beyond planning - automated content structuring
- Enhanced document analysis and generation
- Custom framework creation
- Professional template generation

### Phase 3: CV Template Processing & Generation
- Upload custom Word templates with Jinja placeholders
- Batch CV processing (PDF/DOCX support)
- AI-powered content extraction and mapping
- Real-time progress tracking
- Instant download of processed documents
- Professional formatting and layout optimization

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **AI Integration**: OpenAI API, Google Gemini API
- **Document Processing**: python-docx, PyPDF2, docxtpl, pdf2docx
- **Real-time Communication**: Flask-SocketIO
- **Authentication**: Flask-JWT-Extended

## Quick Start

### Option 1: One-Command Setup (Recommended)
```bash
python quick_start.py
```
This script will:
- Check Python version
- Create virtual environment
- Install dependencies
- Set up directories
- Create configuration files
- Start the application

### Option 2: Manual Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd BIGPIAI
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

### Local Development
```bash
# Option 1: Use the development runner
python run_local.py

# Option 2: Use the batch file (Windows)
run_local.bat

# Option 3: Direct Flask run
python run.py
```

### Production Deployment

#### Single VM Deployment (Linux)
```bash
# Make script executable
chmod +x deploy_vm.sh

# Deploy with default settings (port 80)
sudo ./deploy_vm.sh

# Deploy on custom port
PORT=8080 ./deploy_vm.sh
```

#### Manual Production Deployment
```bash
# Option 1: Interactive deployment menu
python deploy_production.py

# Option 2: Direct gunicorn (recommended)
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:80 run:app
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
FLASK_ENV=development

# Production Settings
PRODUCTION=false
USE_WAITRESS=false

# AI Configuration (Required for Phase 3)
GEMINI_API_KEY=your-gemini-api-key-here

# Server Configuration
HOST=0.0.0.0
PORT=5000
```

### Required API Keys

- **Gemini API Key**: Required for Phase 3 CV processing
  - Get your key from: https://makersuite.google.com/app/apikey
  - Add to `.env` file as `GEMINI_API_KEY=your-key-here`

## Usage

1. Start the application using one of the run methods above
2. Navigate to `http://localhost:5000` (or your configured port)
3. Choose your processing phase:
   - **Phase 1**: Document analysis and writing plan generation
   - **Phase 2**: Advanced template and content generation
   - **Phase 3**: CV template processing with custom templates
4. Upload your documents
5. Monitor processing progress
6. Download the processed results

## API Endpoints

### Phase 1 & 2
- `POST /upload-phase1` - Phase 1 document processing
- `POST /upload-phase2` - Phase 2 advanced processing

### Phase 3 (CV Processing)
- `POST /phase3/process` - Process CV files with template
- `GET /phase3/download/<file_id>` - Download processed document
- `GET /phase3/status/<session_id>` - Check processing status

### General
- `GET /` - Main application interface
- `POST /login` - User authentication
- `GET /logout` - User logout

## File Structure

```
BIGPIAI/
├── app/
│   ├── templates/
│   │   └── home/
│   │       ├── sectionphase1.html
│   │       ├── sectionphase2.html
│   │       └── sectionphase3.html
│   ├── routes/
│   │   ├── phase3.py
│   │   └── ...
│   └── cv_processor/
│       └── core.py
├── uploads/           # File uploads
├── outputs/           # Processed files
├── run_local.py       # Local development runner
├── run_local.bat      # Windows batch runner
├── deploy_vm.sh       # VM deployment script
├── deploy_production.py # Production deployment
├── quick_start.py     # One-command setup
└── requirements.txt   # Dependencies
```

## Development

### Local Development
```bash
# Use the development runner with auto-reload
python run_local.py

# Or set environment variables manually
export FLASK_ENV=development
export FLASK_DEBUG=1
python run.py
```

### Adding New Features
1. Create feature branch
2. Add routes in `app/routes/`
3. Add templates in `app/templates/`
4. Update requirements if needed
5. Test locally with `python run_local.py`

## Production Deployment Options

### 1. VM Deployment (Recommended)
```bash
sudo ./deploy_vm.sh
```
- Automatic system setup
- Nginx reverse proxy
- Systemd service
- SSL ready

### 2. Docker Deployment
```bash
# Build image
docker build -t bigpiai .

# Run container
docker run -p 80:5000 -e PRODUCTION=true bigpiai
```

### 3. Manual Server Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run with gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:80 run:app
```

## Troubleshooting

### Common Issues

1. **Port 80 Permission Denied**
   ```bash
   # Use different port
   PORT=8080 ./deploy_vm.sh
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **AI Processing Errors**
   - Check `GEMINI_API_KEY` in `.env` file
   - Verify API key is valid and has quota

4. **File Upload Issues**
   - Check upload directory permissions
   - Verify file size limits in configuration

### Logs
- Development: Console output
- Production: `logs/access.log` and `logs/error.log`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python run_local.py`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.