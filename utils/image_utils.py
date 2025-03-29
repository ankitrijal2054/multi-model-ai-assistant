import base64

def image_to_base64(file_bytes) -> str:
    return base64.b64encode(file_bytes).decode('utf-8')

