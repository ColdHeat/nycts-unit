import Image
import ImageDraw
import time

def draw(direction, constants, config, train_data, train_directions, matrix):
    image = Image.new('RGB', (constants.width, constants.height))
    draw = ImageDraw.Draw(image)
    #customer_retention = config['settings']['customer_retention']
    #schedule_length = range(len(train_data[direction]['schedule']))

    if direction in train_directions:
        for destination in train_data[direction]:
            index_range = destination[1:3:]
            #if customer_retention == True:
            #    index_range = schedule_length[1:3:]
            #else:
            #    index_range = schedule_length[0:2:]

            for row in index_range:
                data = train_data[direction][destination]['schedule'][row]
                xOff = 0
                yOff = -1
                mins = str(data['arrivalTime'])
                if len(mins) < 2:
                    mins = mins.rjust(3)

                minLabel = 'Min'
                dirLabel = train_data[direction][destination]['term'] + ' '
                if row == 1:
                    yOff = 15

                fontXoffset = xOff
                fontYoffset = yOff
                minPos = constants.width \
                    - constants.font.getsize(minLabel)[0] - 3
                minOffset = constants.width - 2 - constants.font.getsize(minLabel)[0]
                time1Offset = 102
                minOffset = constants.width - 2 - constants.font.getsize(minLabel)[0]
                draw.text((fontXoffset, fontYoffset), dirLabel, font=constants.font, fill=constants.red)
                if mins == "Leaving":
                    time1Offset = 95
                draw.text((time1Offset, fontYoffset), mins, font=constants.font, fill=constants.red)
                if mins != "Leaving":
                    draw.text((minOffset, fontYoffset), minLabel, font=constants.font, fill=constants.red)
                draw.text((fontXoffset, fontYoffset + 7), data['length'] + ' CAR TRAIN', font=constants.font, fill=constants.orange)

            matrix.SetImage(image, 0, 0)
            time.sleep(config['settings']['transition_time'])
