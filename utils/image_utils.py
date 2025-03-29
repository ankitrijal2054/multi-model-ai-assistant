import base64

def image_to_base64(image_file) -> str:
    return base64.b64encode(image_file.read()).decode('utf-8')
