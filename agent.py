import csv
from swarm import Swarm, Agent
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from textwrap import wrap

client = Swarm()

def read_csv_to_string(file_path: str) -> str:
    lines = []
    with open(file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            time = row['Time']
            x = row['X']
            y = row['Y']
            name = row['Object Name']
            status = row['Object Status']
            lines.append(f"{time},{x},{y},{name},{status}")
    return "\n".join(lines)

def save_text_to_pdf(text: str, filename: str):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    x_margin = 50
    y = height - 50
    line_height = 16

    for paragraph in text.split("\n\n"):
        wrapped_lines = []
        for line in paragraph.split("\n"):
            wrapped_lines += wrap(line, width=90)
        for line in wrapped_lines:
            if y <= 50:
                c.showPage()
                y = height - 50
            c.drawString(x_margin, y, line)
            y -= line_height
        y -= line_height

    c.save()

def generate_description_from_csv(file_path: str):

    input_data = read_csv_to_string(file_path)

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

    save_text_to_pdf(result, "output.pdf")
    print("\nPDF saved as 'output.pdf' in the current directory.")


if __name__ == "__main__":
    generate_description_from_csv("input.csv")
