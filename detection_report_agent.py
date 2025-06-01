import csv
from swarm import Swarm, Agent
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from textwrap import wrap
import os

client = Swarm()

def read_csv_data(file_path: str):
    input_lines = []
    image_paths = []
    with open(file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            timestamp = row['Timestamp']
            obj_class = row['Object Class']
            image_path = row.get('Image Path', "").strip()
            input_lines.append(f"{timestamp},{obj_class}")
            image_paths.append(image_path if os.path.exists(image_path) else None)

    # Debug print
    for i, path in enumerate(image_paths):
        print(f"Image {i + 1}: {path if path else 'Not found or not provided.'}")

    return "\n".join(input_lines), image_paths


def save_text_to_pdf(text: str, image_paths: list[str], filename: str):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    x_margin = 50
    line_height = 16
    title = "Object Detection Report"

    # Title Page
    y = height - 50
    title_font_size = 20
    c.setFont("Helvetica-Bold", title_font_size)
    c.drawCentredString(width / 2, y, title)
    y -= (title_font_size + 40)

    intro = "This report contains object detection data collected from the sensor. Each object is listed with its timestamp and name. Associated images, if available, are also included."
    c.setFont("Helvetica", 12)
    for line in wrap(intro, width=90):
        c.drawString(x_margin, y, line)
        y -= line_height

    c.showPage()

    entries = text.strip().split("\n\n")

    for index, paragraph in enumerate(entries):
        y = height - 50
        c.setFont("Helvetica", 12)

        for line in wrap(paragraph, width=90):
            c.drawString(x_margin, y, line)
            y -= line_height

        if index < len(image_paths) and image_paths[index]:
            try:
                img = ImageReader(image_paths[index])
                img_width = 200
                img_height = 150
                if y - img_height < 50:
                    y -= img_height
                c.drawImage(image_paths[index], x_margin, y - img_height, width=img_width, height=img_height)
            except Exception as e:
                print(f"Failed to add image for entry {index + 1}: {e}")

        c.showPage()

    c.save()

def generate_description_from_csv(file_path: str):
    input_data, image_paths = read_csv_data(file_path)

    messages = [
    {
        "role": "user",
        "content": f"""
You will receive comma-separated object detection data in the format:
timestamp, object class

Each line represents one detected object. For each item, write an English sentence describing the detection. Include index numbers on each item.

Input:
{input_data}
"""
    }
]

    description_agent = Agent(
        name="Object Description Agent",
        instructions="You are a helpful assistant that converts object detection logs into formal English sentences.",
    )

    response = client.run(agent=description_agent, messages=messages)
    result = response.messages[-1]["content"]

    print(result)

    save_text_to_pdf(result, image_paths, "object_detection_report.pdf")
    print("\nPDF saved as 'object_detection_report.pdf' in the current directory.")


if __name__ == "__main__":
    generate_description_from_csv("detection_log.csv")
