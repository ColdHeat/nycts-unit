import Image

pic = Image.open("emoji.gif")
pic = pic.convert('RGB')
pic.thumbnail((128,32), Image.ANTIALIAS)
