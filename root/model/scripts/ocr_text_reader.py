import numpy
import pytesseract, logging
from PIL import ImageGrab
import pyautogui

logger = logging.getLogger('OCR text reader')
pytesseract.pytesseract.tesseract_cmd = 'c:/Program Files/Tesseract-OCR/tesseract'


# def return_text(coordinates, grayscale=False):
    # '''
    # coordinates = dict(top, left, width, height)
    # Found at the internet as well.
    # grab screen part and read its text contents
    # No regex or text formating implemented.

    # Greyscale is on to increase speed
    # '''
    # with mss.mss() as sct:
    #     im = numpy.asarray(sct.grab(coordinates))
    #     if grayscale:
    #         im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    #     text = pytesseract.image_to_string(im)
    #     print(text)
        # debugging purpusess
        # cv2.imshow('Image', im)
        # if cv2.waitKey(25) & 0xFF == ord('q'):
        #     cv2.destroyAllWindows()
        #     raise Exception('Interrupted by user')
    # return text


def return_text(coordinates, grayscale=False):
    '''
    coordinates = dict(top, left, width, height)
    Found at the internet as well.
    grab screen part and read its text contents
    No regex or text formating implemented.

    Greyscale is on to increase speed
    '''
    text = ''
    try:
        image = ImageGrab.grab(bbox=(coordinates['left'],
                        coordinates['top'], 
                        coordinates['left'] + coordinates['width'], 
                        coordinates['top'] + coordinates['height']), 
                        all_screens=True)
        converted = numpy.asarray(image)
        text = pytesseract.image_to_string(converted)
    except Exception as error:
        raise Exception(f'Could not ready image text due {error}')
    print(f'Text found: {text}')
    return text


def image_grab_text(coordinates, grayscale=False):
    '''
    coordinates = dict(top, left, width, height)
    Found at the internet as well.
    grab screen part and read its text contents
    No regex or text formating implemented.

    Greyscale is on to increase speed
    '''
    try:
        image = ImageGrab.grab(bbox=(coordinates['left'],
                        coordinates['top'], 
                        coordinates['left'] + coordinates['width'], 
                        coordinates['top'] + coordinates['height']), 
                        all_screens=True)
    except Exception as error:
        raise Exception(f'Could not ready image text due {error}')
    print(f'Image found')
    return



def coordinates_combiner(box_coord1=dict, box_coord2=dict):
    '''
    Transform two image results position into one, getting the position for the first one until the later
    Good for later text or image search in pre defined position.
    '''

    box = {}
    box['left'] = int(box_coord1.left)
    box['top'] = int(box_coord1.top)
    box['height'] = int(box_coord1.height if box_coord1.height > box_coord2.height else box_coord2.height)
    if box_coord1.top < 0:
        box['height'] = int(abs(box_coord1.top) - abs(box_coord2.top) + box_coord1.height + box_coord2.height)
    else:
        box['height'] = int(abs(box_coord2.top) - abs(box_coord1.top) + box_coord1.height + box_coord2.height)
    if box_coord1.left < 0:
        box['width'] = int(abs(box_coord1.left) - abs(box_coord2.left) + box_coord1.width + box_coord2.width)
    else:
        box['width'] = int(abs(box_coord2.left) - abs(box_coord1.left) + box_coord1.width + box_coord2.width)
    return box

