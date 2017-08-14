import socket
from display import *

def config_matrix(b, config, logger):
    dev = config["dev"]
    swap = b.matrix.CreateFrameCanvas()
    transition_time = int(config["transition_time"])
    b.matrix.brightness = int(config["brightness"])
    try:
        swap.Clear()
        swapImage = display.Image.new('RGB', (width, height))
        swapDraw  = display.ImageDraw.Draw(swapImage)
        if dev == True:
            try:
                ip = str([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
                logger.info('IP screen', extra={'status': 1, 'job': 'boot_screen'})
            except Exception as e:
                logger.info('IP screen', extra={'status': 0, 'job': 'boot_screen'})
                ip = '192.168.0.xxx'

            swapDraw.text((2, 0), 'IP: ' + ip , font=display.font, fill=display.red)
        else:
            logger.info('NYC Train Sign', extra={'status': 1, 'job': 'boot_screen'})
            swapDraw.text((2, 0), 'NYC TRAIN SIGN'  , font=display.font, fill=display.red)
            swapDraw.text((68, 0), ' legit. realtime.'  , font=display.font, fill=display.green)
            swapDraw.text((2, 16), '@' , font=display.font, fill=display.green)
            swapDraw.text((12, 16), 'n y c t r a i n s i g n' , font=display.font, fill=display.orange)


    swap.SetImage(swapImage, 0, 0)
    time.sleep(transition_time)
    swap = b.matrix.SwapOnVSync(swap)
