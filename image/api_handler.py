import runpod
from ImageGenerator import ImageGenerator
import json
def process_image(job):   
    try:
        generator = ImageGenerator()
        return generator.edit_image(job["input"]['input_image'], job["input"]['prompt'], job["input"]['model'])
    except (json.JSONDecodeError, Exception) as error:
        return 'error: ' + str(error)

runpod.serverless.start({"handler": process_image})