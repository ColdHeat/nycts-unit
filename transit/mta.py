def draw(self, direction):
    self.config = self.base.config
    image = Image.new('RGB', (constants.width, constants.height))
    draw = ImageDraw.Draw(image)
    customer_retention = self.config['settings']['customer_retention']
    schedule_length = range(len(self.train_data[direction]['schedule']))

    if direction in self.train_directions:
        if customer_retention == True:
            index_range = schedule_length[1:3:]
        else:
            index_range = schedule_length[0:2:]

        for row in index_range:
            self.data = self.train_data[direction]['schedule'][row]
            xOff = 2
            yOff = 2

            mins = str(self.data['arrivalTime'])
            if len(mins) < 2:
                mins = mins.rjust(3)

            minLabel = 'Min'
            dirLabel = '  ' + self.train_data[direction]['term']

            nums = self.data['routeId']

            if nums in ['1', '2', '3']:
                circleColor = constants.red
            if nums in ['4', '5', '6']:
                circleColor = constants.green
            if nums in ['G']:
                circleColor = constants.g_green
            if nums in ['N', 'Q', 'R', 'W']:
                circleColor = constants.yellow
            if nums in ['A', 'C', 'E', 'SI']:
                circleColor = constants.blue
            if nums in ['J', 'Z']:
                circleColor = constants.brown
            if nums in ['7']:
                circleColor = constants.purple
            if nums in ['B', 'D', 'F', 'M']:
                circleColor = constants.orange
            if nums in ['L']:
                circleColor = constants.grey

            if row == 1:
                yOff = 18

            fontXoffset = xOff
            fontYoffset = yOff

            numLabel = str(row + 1) + '. '
            numLabelW = constants.font.getsize(numLabel)[0]

            minPos = constants.width \
                - constants.font.getsize(minLabel)[0] - 3

            circleXoffset = fontXoffset + numLabelW - 6
            circleYoffset = yOff + 1

            circleXend = circleXoffset + 8
            circleYend = circleYoffset + 8

            minOffset = constants.width - 6 \
                - constants.font.getsize(minLabel)[0]
            timeOffset = minOffset - constants.font.getsize(mins)[0]
            draw.ellipse((circleXoffset, circleYoffset, circleXend,
                circleYend), fill=circleColor)
            draw.text((circleXoffset + 1, circleYoffset - 2), nums,
                font=constants.font, fill=constants.black)
            draw.text((circleXend, fontYoffset), dirLabel,
                font=constants.font, fill=constants.green)
            draw.text((timeOffset, 0 + fontYoffset), mins,
                font=constants.font, fill=constants.orange)
            draw.text((minOffset, 0 + fontYoffset), minLabel,
                font=constants.font, fill=constants.green)


        self.base.matrix.SetImage(image, 0, 0)
        time.sleep(self.base.getTransitionTime())
