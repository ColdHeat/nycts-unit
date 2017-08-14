def displayError(e):
    drawClear()
    draw.text((0 + fontXoffset + 3, 0 + topOffset + 0), e, font=font, fill=orange)
    b.matrix.SetImage(image, 0, 0)
    time.sleep(transition_time)
    drawClear()

def error(e):
    logging.exception("message")
    logger.info('Boot Screen', extra={'status': 1, 'job': 'boot_screen'})
    displayError(e)
    pass
