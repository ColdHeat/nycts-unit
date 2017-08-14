class train:

    def initialize_train():
        # determine what train lines are needed. not sure if this is coming from config or not.
        load_train_screen_data()

    def load_train_data():
        swap.Clear()
        count = not count

        try:
            connection = urllib2.urlopen('http://riotpros.com/mta/v1/?client=' + client)
            logger.info('Train Screen', extra={'status': 1, 'job': 'train_screen'})
        except urllib2.URLError as e:
            error_message = e.reason
            logger.info('Train Screen', extra={'status': 0, 'job': 'train_screen', 'error': error_message})

        load_train_screen()

    def load_train_screen():
        if count == True:
            frame = 'ln'
        else :
            frame ='ls'

        if frame == 'ln':
            dirLabel = '    MANHATTAN '
            dirOffset = 22
        if frame == 'ls':
            dirLabel = '   ROCKAWAY PKWY'
            dirOffset = 12

            if frame == 'ln':
                min1 = row_1_train_offline_data['min1'] - loop_count
                min2 = row_1_train_offline_data['min2'] - loop_count

                row_1_train_offline_data['min1'] = min1
                row_1_train_offline_data['min2'] = min2
            if frame == 'ls':
                min1 = row_2_train_offline_data['min1'] - loop_count
                min2 = row_2_train_offline_data['min2'] - loop_count

                row_2_train_offline_data['min1'] = min1
                row_2_train_offline_data['min2'] = min2
        else:
            raw = connection.read()
            times = raw.split()
            connection.close()

        if len(times) > 3:
            try:
                val = int(times[0])
            except ValueError:
                min1 = '*'
                min2 = '*'

            if frame == 'ln':
                min1 = times[0]
                min2 = times[1]

            if frame == 'ls':
                min1 = times[2]
                min2 = times[3]
        else:
            min1 = '*'
            min2 = '*'

        if len(min1) < 2:
            min1 = min1.rjust(3)
        time1Offset = minOffset - font.getsize(min1)[0]

        if len(min2) < 2:
            min2 = min2.rjust(3)
        time2Offset = minOffset - font.getsize(min2)[0]

        dirLabelw = font.getsize(dirLabel)[0]
        draw.rectangle((0, 0, width, height), fill=black)
        draw.text((lOffset, 0 + topOffset), lLabel, font=font, fill=orange)
        draw.text((fontXoffset + dirOffset, 0 + topOffset), dirLabel, font=font, fill=green)
        draw.text((time1Offset, 0 + topOffset), min1, font=font, fill=orange)
        draw.text((minOffset, 0 + topOffset), minLabel, font=font, fill=green)

        draw.text((lOffset, 16), lLabel, font=font, fill=orange)
        draw.text((fontXoffset + dirOffset, 16), dirLabel, font=font, fill=green)
        draw.text((time2Offset, 16), min2, font=font, fill=orange)
        draw.text((minOffset, 16), minLabel, font=font, fill=green)

        draw.point((width - 12, 7), fill=black)
        draw.point((width - 12, 20), fill=black)

        swap.SetImage(image, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)

        swap.Clear()
        swap.SetImage(pic.convert('RGB'), 0, 0)

        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)

        if loop_count == 4:
            loop_count -= 4
        else:
            loop_count += 1
