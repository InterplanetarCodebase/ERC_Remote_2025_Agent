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
            time = row['Time']
            x = row['X']
            y = row['Y']
            name = row['Object Name']
            status = row['Object Status']
            image_path = row.get('ImagePath', "").strip()
            input_lines.append(f"{time},{x},{y},{name},{status}")
            image_paths.append(image_path if os.path.exists(image_path) else None)

    # printing image paths for debugging
    for i, path in enumerate(image_paths):
        if path:
            print(f"Image {i + 1}: {path}")
        else:
            print(f"Image {i + 1}: Not found or not provided.")

    return "\n".join(input_lines), image_paths

def save_text_to_pdf(text: str, image_paths: list[str], filename: str):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    x_margin = 50
    line_height = 16
    title = "Object Detection Report"

    # First Page - Title Page
    y = height - 50
    title_font_size = 20
    c.setFont("Helvetica-Bold", title_font_size)
    c.drawCentredString(width / 2, y, title)
    y -= (title_font_size + 40)

    intro = "This report contains the object detection data collected from the sensor. Each object is described in detail, including its position and status."
    c.setFont("Helvetica", 12)
    for line in wrap(intro, width=90):
        c.drawString(x_margin, y, line)
        y -= line_height

    c.showPage()  # Move to next page for first object

    # Process each object (1 object per page)
    entries = text.strip().split("\n\n")

    for index, paragraph in enumerate(entries):
        y = height - 50
        c.setFont("Helvetica", 12)

        # Draw the text
        for line in wrap(paragraph, width=90):
            c.drawString(x_margin, y, line)
            y -= line_height

        # Insert image
        if index < len(image_paths) and image_paths[index]:
            img_path = image_paths[index]
            try:
                img = ImageReader(img_path)
                img_width = 200
                img_height = 150
                if y - img_height < 50:
                    y -= img_height  # move further down if space is limited
                c.drawImage(img_path, x_margin, y - img_height, width=img_width, height=img_height)
            except Exception as e:
                print(f"Failed to add image for entry {index + 1}: {e}")

        c.showPage()  # Next object gets a new page

    c.save()

def generate_description_from_csv(file_path: str):
    input_data, image_paths = read_csv_data(file_path)

    messages = [
        {
            "role": "user",
            "content": f"""
You will receive comma-separated object detection data in the format:
time, x, y, object name, status

Each line represents one object. Create a English sentence describing each detected object. If the status was N/A write that no additional information was found,Include index numbers on each item.

Input:
{input_data}
"""
        }
    ]

    description_agent = Agent(
        name="Object Description Agent",
        instructions="You are a helpful assistant that converts raw sensor data into clear, formal object descriptions.",
    )

    response = client.run(agent=description_agent, messages=messages)
    result = response.messages[-1]["content"]

    print(result)

    save_text_to_pdf(result, image_paths, "object_detection_report.pdf")
    print("\nPDF saved as 'object_detection_report' in the current directory.")


if __name__ == "__main__":
    generate_description_from_csv("detection_log.csv")
