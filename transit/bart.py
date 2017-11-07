import Image
import ImageDraw

def draw(direction, constants, config, train_data, train_directions, matrix):
    image = Image.new('RGB', (constants.width, constants.height))
    draw = ImageDraw.Draw(image)
    customer_retention = config['settings']['customer_retention']
    schedule_length = range(len(train_data[direction]['schedule']))

    if direction in train_directions:
        if customer_retention == True:
            index_range = schedule_length[1:3:]
        else:
            index_range = schedule_length[0:2:]

        for row in index_range:
            data = train_data[direction]['schedule'][row]
            xOff = 2
            yOff = 2

            mins = str(data['arrivalTime'])
            if len(mins) < 2:
                mins = mins.rjust(3)

            minLabel = 'Min'
            dirLabel = '  ' + train_data[direction]['term']
            if row == 1:
                yOff = 18

            fontXoffset = xOff
            fontYoffset = yOff

            numLabel = str(row + 1) + '. '
            numLabelW = constants.font.getsize(numLabel)[0]

            minPos = constants.width \
                - constants.font.getsize(minLabel)[0] - 3

            time1Offset = 106
            minOffset = constants.width - 2 - constants.font.getsize(minLabel)[0]
            dirLabelw = constants.font.getsize(dirLabel)[0]
            draw.rectangle((0, 0, constants.width, constants.height), fill=constants.black)
            draw.text((fontXoffset + 2, -1), 'DALY CITY', font=constants.font, fill=constants.red)
            draw.text((time1Offset, -1), mins, font=constants.font, fill=constants.red)
            draw.text((minOffset, -1), minLabel, font=constants.font, fill=constants.red)
            draw.text((fontXoffset + 2, 6), '8 CAR TRAIN', font=constants.font, fill=constants.orange)

        matrix.SetImage(image, 0, 0)
