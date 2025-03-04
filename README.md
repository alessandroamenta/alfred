# Alfred - Hotel Assistant Knowledge Base Manager

A Python-based tool for managing knowledge bases for hotel assistants using the Vapi.ai API. This project helps create and update knowledge bases for hotel concierge services, specifically designed for the Bella Vista Suites hotel.

## Features

- Create knowledge bases using the Vapi.ai API
- Update existing assistants with new knowledge base configurations
- Manage hotel-specific information and room details
- Configure search parameters for optimal response quality

## Setup

1. Clone the repository:

```bash
git clone https://github.com/alessandroamenta/alfred.git
cd alfred
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your Vapi.ai API key in the `knowledge_base.py` file or as an environment variable.

## Usage

Run the knowledge base manager:

```bash
python knowledge_base.py
```

## Configuration

The script uses the following configuration:

- Vapi.ai API endpoint: https://api.vapi.ai
- Knowledge base provider: Trieve
- Search configuration: Hybrid search with topK=5

## Project Structure

- `knowledge_base.py`: Main script for managing knowledge bases
- `requirements.txt`: Project dependencies
- `README.md`: Project documentation

## License

MIT License
