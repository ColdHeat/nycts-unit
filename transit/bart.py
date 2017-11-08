import Image
import ImageDraw
import time

def draw(swap, direction, constants, config, train_data, train_directions, matrix):
    image = Image.new('RGB', (constants.width, constants.height))
    draw = ImageDraw.Draw(image)
    if direction in train_directions:
        destination_length = range(len(train_data[direction]))


        for destination in destination_length:
            schedule_length = range(len(train_data[direction][destination]['schedule']))

            index_range = schedule_length[0:2:]
            swap.Clear()
            #draw.rectangle((0, 0, constants.width, constants.height), fill=constants.black)
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
        if destination != (len(train_data[direction])-1):
            time.sleep(int(config['settings']['transition_time']))
