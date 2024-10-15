# waifuc_booru_crawler_GUI
This is a GUI wrapper for [waifuc](https://github.com/deepghs/waifuc).  
Tested on Python 3.10 at Windows environment.  
  
How to run
1. [Download this repository as a zip file](https://github.com/david419kr/waifuc_booru_crawler_GUI/archive/refs/heads/main.zip), or "git clone https://github.com/david419kr/waifuc_booru_crawler_GUI.git"
2. Run 0_install.bat
3. Run 1_start_gui.bat

# Features
Features are simple and limited.  
While [original waifuc](https://github.com/deepghs/waifuc) has tons of features, I only implemented features that I use personally.  
  
![image](https://github.com/user-attachments/assets/f53a6468-174c-4409-a9b7-32943f561b3f)

Source:  
Selectable from Danbooru and Gelbooru.  
![image](https://github.com/user-attachments/assets/5b7b3607-c08e-449d-bc90-2826a52617e2)

Search Term:  
Your search term. If source is Danbooru, search terms are limited as 2 words.  
Supports autocomplete feature from danbooru.csv, which is included.  
Each terms are separated by ' '(space bar). It's same as searching at booru sites.  
![image](https://github.com/user-attachments/assets/27e5975a-f9d3-4e11-acb0-3081a7c224e5)  


Resize size:  
If the image is too large, it will be resized based on the shorter side of the x and y dimensions, according to the specified number.  
  
Enable Tagging:  
Automatically tags images. Same as Tagger in SD-webui.  
  
Max Crawling Count:  
Stop crawling when reached this number.  
  
Ouput Path:  
Your desired output folder path.
