# Dr. Clivi - Multi-Agent Healthcare Assistant

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![ADK](https://img.shields.io/badge/ADK-v1.0.0-green.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

## Overview

Dr. Clivi is a sophisticated multi-agent healthcare assistant built with Google's Agent Development Kit (ADK). Originally migrated from Dialogflow CX, this system provides specialized support for diabetes and obesity management via WhatsApp.

### Key Features

- 🤖 **Multi-Agent Architecture**: Specialized agents for diabetes and obesity flows
- 🔄 **A2A Protocol**: Agent-to-agent communication for complex workflows  
- 📱 **WhatsApp Integration**: Native messaging support via Twilio
- 🏥 **Healthcare Focused**: Evidence-based medical guidance and support
- ☁️ **Vertex AI Ready**: Optimized for deployment on Google Cloud
- 🔒 **HIPAA Considerations**: Privacy and security-first design

### Architecture

```
Dr. Clivi System
├── Coordinator Agent (Main Router)
├── Diabetes Flow Agent (Glucose management, education)
├── Obesity Flow Agent (Weight management, nutrition)
└── Integration Layer (WhatsApp, Clivi API, A2A)
```

## Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud Project with Vertex AI enabled
- Poetry for dependency management
- Twilio account for WhatsApp (optional for development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/GibrannClivi/dr-clivi.git
   cd dr-clivi
   ```

2. **Set up the environment**
   ```bash
   cd drClivi
   poetry install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run the agent**
   ```bash
   poetry run adk run .
   ```

### Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token

# Clivi API
CLIVI_API_BASE_URL=your-api-url
CLIVI_API_KEY=your-api-key
```

## Project Structure

```
drClivi/
├── dr_clivi/
│   ├── __init__.py
│   ├── agent.py              # Main coordinator agent
│   ├── config.py             # Configuration management
│   ├── prompts.py            # Agent instructions and prompts
│   ├── agents/               # Specialized agent implementations
│   ├── flows/                # Diabetes and obesity flows  
│   ├── tools/                # Custom tools and integrations
│   └── integrations/         # External service integrations
├── tests/                    # Unit and integration tests
├── eval/                     # Agent evaluation scripts
├── deployment/               # Deployment configurations
├── pyproject.toml           # Dependencies and project config
└── README.md
```

## Features by Flow

### Diabetes Management
- 📊 Glucose monitoring and trend analysis
- 💊 Medication reminders and information
- 🍎 Diabetic nutrition guidance
- ⚠️ Hypoglycemia/hyperglycemia alerts
- 📚 Diabetes education and support

### Obesity Management  
- 📏 BMI calculation and tracking
- 🥗 Personalized nutrition plans
- 🏃‍♀️ Exercise recommendations
- 📈 Weight loss progress monitoring
- 🧠 Behavioral change support

## Deployment

### Local Development
```bash
poetry run adk run .
```

### Vertex AI Agent Engine
```bash
poetry run python deployment/deploy.py
```

### Docker/Cloud Run
```bash
docker build -t dr-clivi .
gcloud run deploy dr-clivi --image dr-clivi
```

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Formatting
```bash
poetry run black dr_clivi/
```

### Evaluation
```bash
poetry run python eval/run_evaluation.py
```

## Migration from Dialogflow CX

This project represents a migration from Dialogflow CX to ADK for enhanced:
- **Flexibility**: Custom agent logic vs. rigid flow structures
- **Intelligence**: Gemini 2.5 native integration
- **Scalability**: Modular architecture and version control
- **Integration**: Native Google Cloud and A2A support

See [MIGRATION.md](MIGRATION.md) for detailed migration strategy.

## Security & Privacy

- 🔐 Environment-based secret management
- 🛡️ HIPAA-compliant data handling considerations
- 🔒 Secure API authentication
- 📋 Audit logging and monitoring
- 🚫 No PII in code or logs

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

For questions or issues:
- 📧 Email: dev@clivi.com
- 🐛 Issues: [GitHub Issues](https://github.com/GibrannClivi/dr-clivi/issues)
- 📖 Documentation: [ADK Docs](https://google.github.io/adk-docs/)

---

**Disclaimer**: Dr. Clivi is an AI assistant for educational and support purposes. It does not replace professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical decisions.
