# Image Quote Generator
This is a Python script that generates an image quote by retrieving a random image from Unsplash and a random quote from the Stoic Quotes API. It then crops the image to a square aspect ratio and adds the quote as text to the center of the image.

## Dependencies
This script requires the following Python packages:

- requests
- Pillow
#### You can install them using pip:

`pip install requests Pillow`
## Usage

1. Create a free account on Unsplash and get an access key.

2. In the main function at the bottom of the code, paste your Unsplash Access Key in the `access_key` variable.

3. In the get_quote function at the top of the code, set your preferred `max_line_length` and `font_size`, and paste your desired font style in the font_style variable.


The generated image quote will be saved in the same directory as the script with a file name in the format my_quote_image.png.
