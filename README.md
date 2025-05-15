 
# <img src="https://trojmiasto.mapaakademicka.pl/wp-content/uploads/sites/6/2023/07/logotyp-PG-i-WETI.jpg" alt="Logo Politechniki Gdańskiej" style="height: 150px;">
### Politechnika Gdańska
#### Wydział Elektroniki, Telekomunikacji i Informatyki  
#### Kierunek: Inżynieria Biomedyczna  
#### Przedmiot: Rozwój Aplikacji Internetowych w Medycynie
#### Prowadzący: *dr inż. Anna Węsierska*  
#### Rok akademicki: **2024/2025**
# Biomedical Engineering Project
## SpermVizz
Interactive website to visualize the sperm segmentation problem in a video sequence - segmentation by parts. 

The aim of the project is to create an interactive website that allows visualization of the sperm segmentation process in video sequences from the ICSI (IntraCytoplasmic Sperm Injection) procedure. 
- Sperm segmentation based on their parts, such as the head and flagellum
- Changing colors of segments
- Uploading video
- Analyzing movement (e.g. direction)
- Tracking a specific sperm cell

### Procject Structure

```txt
.
├── app                            Responsible for the web application
│   ├── main.py
│   ├── static
│   │   ├── Fonts
│   │   ├── IMG
│   │   ├── style2.css
│   │   ├── style3.css
│   │   ├── style.css
│   │   └── uploads
│   └── templates
│       ├── index.html
│       ├── logowanie.html
│       ├── register.html
│       ├── segmentacja.html
│       └── wideo.html
├── dataset                        Photos and videos needed for segmentation
│   ├── private
        ------
│   └── public
│       └-----
├── README.md
├── requirements.in
├── requirements.txt
└── video_processing                Responsible for video processing and segmentation
    ├── model
    ├── my_model
    │   ├── LoadDataset.py
    │   ├── seg-unet.py
    │   ├── sperm_unet_2channels.pth
    │   ├── train.py
    │   ├── unet_model.py
    │   └── unet_parts.py
    ├── sam_vit_b_01ec64.pth
    ├── sam_vit_h_4b8939.pth
    └── segmentation.py

```

### Technologies used
- Flask
- MySQL/SQLAlchemy
- HTML5/CSS/JavaScript
- Pytorch

More info in `requirements.txt`

### GUI (prototype)

![Untitled](https://github.com/user-attachments/assets/37b6cae7-a978-4fa2-9bfe-8145c8d589e5)
![obraz](https://github.com/user-attachments/assets/5a5d2faa-5167-4d0a-97a3-1ab627c32c60)

### Launching project
Visit:
https://spermvizz.onrender.com/

#### To launch locally
Website
- run `python3 main.py`

Testing models
- make sure to change file path
- run `python3 segmentation.py` or `python3 seg-unet.py`

## Authors
- Urszula Plec
- Weronika Woźniak
