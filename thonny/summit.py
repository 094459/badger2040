import badger2040
import badger_os
import qrcode
import time
import os

WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT

IMAGE_WIDTH = 104

COMPANY_HEIGHT = 30
DETAILS_HEIGHT = 20
NAME_HEIGHT = HEIGHT - COMPANY_HEIGHT - (DETAILS_HEIGHT * 2) - 2
TEXT_WIDTH = WIDTH - IMAGE_WIDTH - 1

# defaults
#COMPANY_TEXT_SIZE = 0.6
#DETAILS_TEXT_SIZE = 0.5

COMPANY_TEXT_SIZE = 0.6
DETAILS_TEXT_SIZE = 0.5

LEFT_PADDING = 5
NAME_PADDING = 20
DETAIL_SPACING = 10

DEFAULT_TEXT = """Ricardo Sueiras
Open Source
Twitter
@094459
Dev Advocate at AWS"""


# Check that the qrcodes directory exists, if not, make it
try:
    os.mkdir("qrcodes")
except OSError:
    pass

# Check that there is a qrcode.txt, if not preload
try:
    text = open("qrcodes/qrcode.txt", "r")
except OSError:
    text = open("qrcodes/qrcode.txt", "w")
    text.write("""https://aws-oss.beachgeek.co.uk/1o0
Open Source @ AWS

AWS Summit Berlin

Scan this code to
learn about 
Open Source
at AWS
""")
    text.flush()
    text.seek(0)

# Load all available QR Code Files
try:
    CODES = [f for f in os.listdir("/qrcodes") if f.endswith(".txt")]
    TOTAL_CODES = len(CODES)
except OSError:
    pass


print(f'There are {TOTAL_CODES} QR Codes available:')
for codename in CODES:
    print(f'File: {codename}')

display = badger2040.Badger2040()
code = qrcode.QRCode()

state = {
    "current_qr": 0
}



BADGE_IMAGE = bytearray(int(IMAGE_WIDTH * HEIGHT / 8))

try:
    open("ricsue.bin", "rb").readinto(BADGE_IMAGE)
except OSError:
    try:
        import badge_image
        BADGE_IMAGE = bytearray(badge_image.data())
        del badge_image
    except ImportError:
        pass

# ------------------------------
#      Utility functions
# ------------------------------

# Reduce the size of a string until it fits within a given width
def truncatestring(text, text_size, width):
    while True:
        length = display.measure_text(text, text_size)
        if length > 0 and length > width:
            text = text[:-1]
        else:
            text += ""
            return text


# ------------------------------
#      Drawing functions
# ------------------------------

# Draw the badge, including user text
def draw_badge():
    display.pen(0)
    display.clear()

    # Draw badge image
    display.image(BADGE_IMAGE, IMAGE_WIDTH, HEIGHT, WIDTH - IMAGE_WIDTH, 0)

    # Draw a border around the image
    display.pen(0)
    display.thickness(1)
    display.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - 1, 0)
    display.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - IMAGE_WIDTH, HEIGHT - 1)
    display.line(WIDTH - IMAGE_WIDTH, HEIGHT - 1, WIDTH - 1, HEIGHT - 1)
    display.line(WIDTH - 1, 0, WIDTH - 1, HEIGHT - 1)

    # Uncomment this if a white background is wanted behind the company
    # display.pen(15)
    # display.rectangle(1, 1, TEXT_WIDTH, COMPANY_HEIGHT - 1)

    # Draw the company
    display.pen(15)  # Change this to 0 if a white background is used
    #display.font("serif")
    display.font("sans")
    display.thickness(3)
    display.text(company, LEFT_PADDING, (COMPANY_HEIGHT // 2) + 1, COMPANY_TEXT_SIZE)

    # Draw a white background behind the name
    display.pen(15)
    display.thickness(1)
    display.rectangle(1, COMPANY_HEIGHT + 1, TEXT_WIDTH, NAME_HEIGHT)

    # Draw the name, scaling it based on the available width
    display.pen(0)
    display.font("sans")
    display.thickness(4)
    name_size = 2.0  # A sensible starting scale
    while True:
        name_length = display.measure_text(name, name_size)
        if name_length >= (TEXT_WIDTH - NAME_PADDING) and name_size >= 0.1:
            name_size -= 0.01
        else:
            display.text(name, (TEXT_WIDTH - name_length) // 2, (NAME_HEIGHT // 2) + COMPANY_HEIGHT + 1, name_size)
            break

    # Draw a white backgrounds behind the details
    display.pen(15)
    display.thickness(1)
    display.rectangle(1, HEIGHT - DETAILS_HEIGHT * 2, TEXT_WIDTH, DETAILS_HEIGHT - 1)
    display.rectangle(1, HEIGHT - DETAILS_HEIGHT, TEXT_WIDTH, DETAILS_HEIGHT - 1)

    # Draw the first detail's title and text
    display.pen(0)
    display.font("sans")
    display.thickness(3)
    name_length = display.measure_text(detail1_title, DETAILS_TEXT_SIZE)
    display.text(detail1_title, LEFT_PADDING, HEIGHT - ((DETAILS_HEIGHT * 3) // 2), DETAILS_TEXT_SIZE)
    display.thickness(2)
    display.text(detail1_text, 5 + name_length + DETAIL_SPACING, HEIGHT - ((DETAILS_HEIGHT * 3) // 2), DETAILS_TEXT_SIZE)

    # Draw the second detail's title and text
    display.thickness(3)
    name_length = display.measure_text(detail2_title, DETAILS_TEXT_SIZE)
    display.text(detail2_title, LEFT_PADDING, HEIGHT - (DETAILS_HEIGHT // 2), DETAILS_TEXT_SIZE)
    display.thickness(2)
    display.text(detail2_text, LEFT_PADDING + name_length + DETAIL_SPACING, HEIGHT - (DETAILS_HEIGHT // 2), DETAILS_TEXT_SIZE)


def measure_qr_code(size, code):
    w, h = code.get_size()
    module_size = int(size / w)
    return module_size * w, module_size


def draw_qr_code(ox, oy, size, code):
    size, module_size = measure_qr_code(size, code)
    display.pen(15)
    display.rectangle(ox, oy, size, size)
    display.pen(0)
    for x in range(size):
        for y in range(size):
            if code.get_module(x, y):
                display.rectangle(ox + x * module_size, oy + y * module_size, module_size, module_size)


def draw_qr_file(n):
    display.led(128)
    file = CODES[n]
    codetext = open("qrcodes/{}".format(file), "r")

    lines = codetext.read().strip().split("\n")
    code_text = lines.pop(0)
    title_text = lines.pop(0)
    detail_text = lines
    
    # Clear the Display
    display.pen(15)  # Change this to 0 if a white background is used
    display.clear()
    display.pen(0)
    

    code.set_text(code_text)
    size, _ = measure_qr_code(128, code)
    left = top = int((badger2040.HEIGHT / 2) - (size / 2))
    draw_qr_code(left, top, 128, code)

    left = 128 + 5

    display.thickness(2)
    display.font("sans")
    display.text(title_text, left, 20, 0.5)
    display.thickness(1)
    

    top = 40
    for line in detail_text:
        display.font("bitmap8")
        display.text(line, left, top, 1)
        top += 10

    if TOTAL_CODES > 1:
        for i in range(TOTAL_CODES):
            x = 286
            y = int((128 / 2) - (TOTAL_CODES * 10 / 2) + (i * 10))
            display.pen(0)
            display.rectangle(x, y, 8, 8)
            if state["current_qr"] != i:
                display.pen(15)
                display.rectangle(x + 1, y + 1, 6, 6)
    display.update()

try:
    badge = open("badge/badge.txt", "r")
except OSError:
    with open("badge/badge.txt", "w") as f:
        f.write(DEFAULT_TEXT)
        f.flush()
    badge = open("badge/badge.txt", "r")

# Read in the next 6 lines
company = badge.readline()        # "mustelid inc"
name = badge.readline()           # "H. Badger"
detail1_title = badge.readline()  # "RP2040"
detail1_text = badge.readline()   # "2MB Flash"
detail2_title = badge.readline()  # "E ink"
detail2_text = badge.readline()   # "296x128px"

# Truncate all of the text (except for the name as that is scaled)
company = truncatestring(company, COMPANY_TEXT_SIZE, TEXT_WIDTH)

detail1_title = truncatestring(detail1_title, DETAILS_TEXT_SIZE, TEXT_WIDTH)
detail1_text = truncatestring(detail1_text, DETAILS_TEXT_SIZE,
                              TEXT_WIDTH - DETAIL_SPACING - display.measure_text(detail1_title, DETAILS_TEXT_SIZE))

detail2_title = truncatestring(detail2_title, DETAILS_TEXT_SIZE, TEXT_WIDTH)
detail2_text = truncatestring(detail2_text, DETAILS_TEXT_SIZE,
                              TEXT_WIDTH - DETAIL_SPACING - display.measure_text(detail2_title, DETAILS_TEXT_SIZE))


badger_os.state_load("qrcodes", state)
changed = not badger2040.woken_by_button()

while True:
    if TOTAL_CODES > 1:
        if display.pressed(badger2040.BUTTON_UP):
            if state["current_qr"] > 0:
                state["current_qr"] -= 1
                changed = True

        if display.pressed(badger2040.BUTTON_DOWN):
            if state["current_qr"] < TOTAL_CODES - 1:
                state["current_qr"] += 1
                changed = True

    if display.pressed(badger2040.BUTTON_B) or display.pressed(badger2040.BUTTON_C):
        display.pen(1)
        display.clear()
        #badger_os.warning(display, "If you have any open source projects you want me to share, contact me via ricsue@amazon.com")
        draw_badge()
        display.update()
        time.sleep(7)
        changed = False
        
    if display.pressed(badger2040.BUTTON_A):
        display.pen(1)
        display.clear()
        #badger_os.warning(display, "If you have any open source projects you want me to share, contact me via ricsue@amazon.com")
        draw_qr_file(state["current_qr"])
        badger_os.state_save("qrcodes", state)
        display.update()
        changed = False
        
    if changed:
        draw_qr_file(state["current_qr"])
        badger_os.state_save("qrcodes", state)
        changed = False

    # Halt the Badger to save power, it will wake up if any of the front buttons are pressed
    display.halt()
