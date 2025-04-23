# Object Description Agent

**Object Description Agent** is a Python project that transforms object detection data from a CSV file into natural language descriptions and compiles them into a PDF report. It leverages **OpenAI's Swarm** for generating formal descriptions and **ReportLab** for PDF generation.

## Features

- Converts tabular object detection data into descriptive text
- Automatically formats descriptions into a clean, professional PDF
- Uses advanced language processing via OpenAI's Swarm

## Requirements

Make sure you have the following installed before running the project:

- **Python 3.10 or higher**
- **`swarm`** – for interacting with OpenAI’s API
- **`reportlab`** – for generating PDFs

**Important:** Don’t forget to **set up your OpenAI API key** before running the agent.

## Input CSV Format

The agent expects a CSV file where each row represents an observed object. Here’s a quick breakdown of the format:


- **Time** – When the object was observed  
- **X, Y** – Coordinates of the object  
- **Object Name** – Name of the detected object  
- **Object Status** – A short note like "Flipped", "Broken", or leave empty if unknown  
- **ImagePath** – Local path to the image of the object

## Usage

1. Place your input CSV in the root directory or adjust the path in the script.
2. Make sure your OpenAI API key is set (`export OPENAI_API_KEY=...` or use a `.env` file).
3. Run the script to generate a PDF with formal descriptions.
