# CGM Meal Annotation Tool  

## Overview  
This project provides a **user-friendly web application** for visualizing and annotating Continuous Glucose Monitor (CGM) data. Users can upload a CGM file, explore glucose trends over time, and manually annotate meal start and end times. The annotated meal events can then be saved and downloaded as a separate file.

## Features  
- **CGM Data Upload**: Users can upload their CGM data file for visualization.  
- **Interactive Visualization**: The glucose levels are plotted with the **x-axis representing time over several weeks**.  
- **Scrolling & Zooming**: Navigate through the plot **daily, weekly, etc.** for detailed analysis.  
- **Manual Annotation**: Mark meal start and end times directly on the plot.  
- **Downloadable Annotations**: Save the annotated meal events as a separate file for further analysis.  

## Installation  

### Prerequisites  
Ensure you have **Python 3.x** installed on your system.  

### Setup  
1. Clone this repository:  
   ```bash
   git clone https://github.com/EleazarMartin/CGM-Meal-Annotation.git
   cd CGM-Meal-Annotation
pip install -r requirements.txt
python CGM_Annotation.py
