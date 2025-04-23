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
    y = height - 50
    line_height = 16
    index = 0

    for paragraph in text.strip().split("\n\n"):
        wrapped_lines = []
        for line in paragraph.split("\n"):
            wrapped_lines += wrap(line, width=90)
        for line in wrapped_lines:
            if y <= 150:
                c.showPage()
                y = height - 50
            c.drawString(x_margin, y, line)
            y -= line_height

        # Image Insertion
        if index < len(image_paths) and image_paths[index]:
            img_path = image_paths[index]
            try:
                img = ImageReader(img_path)
                img_width = 200
                img_height = 150
                if y <= 200:
                    c.showPage()
                    y = height - 50
                c.drawImage(img, x_margin, y - img_height, width=img_width, height=img_height)
                y -= (img_height + 10)
            except Exception as e:
                print(f"Failed to add image for entry {index + 1}: {e}")
                y -= 10

        y -= line_height
        index += 1

    c.save()

def generate_description_from_csv(file_path: str):
    input_data, image_paths = read_csv_data(file_path)

    messages = [
        {
            "role": "user",
            "content": f"""
You will receive comma-separated object detection data in the format:
time, x, y, object name, status

Each line represents one object. Create a English sentence describing each detected object. If the status was N/A write that no additional information was found

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

    save_text_to_pdf(result, image_paths, "output.pdf")
    print("\nPDF saved as 'output.pdf' in the current directory.")


if __name__ == "__main__":
    generate_description_from_csv("input.csv")
