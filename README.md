# SpermVizz
Interactive website to visualize the sperm segmentation problem in a video sequence - segmentation by parts. 

The aim of the project is to create an interactive website that allows visualization of the sperm segmentation process in video sequences from the ICSI (IntraCytoplasmic Sperm Injection) procedure. 
- Sperm segmentation based on their parts, such as the head and flagellum
- Changing colors of segments
- Uploading video
- Analyzing movement (e.g. direction)
- Tracking a specific sperm cell

## Procject Structure
```txt
├── app                      Responsible for the web application
│   ├── main.py
│   ├── static
│   │   └── style.css
│   └── templates
│   	└── index.html
├── dataset                  Photos and videos needed for segmentation
│   ├── private
│   │   └── -------------
│   └── public
│   	└── 194_5119_1.png
├── README.md
└── video_processing         Responsible for video processing and segmentation
	└── segmentation.py
```
## GUI (prototype)

![Untitled](https://github.com/user-attachments/assets/37b6cae7-a978-4fa2-9bfe-8145c8d589e5)
