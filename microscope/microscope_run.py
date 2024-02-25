import microscope_moves as mm

#example position A, define accordingly
posA = {'y': 118.73874999999998, 'z': -24.0725, 'x': 39.45625}
#move to posA and scan 4 slides
mm.image_pos(posA)

#example position A, define accordingly
posA = {'y': 118.73874999999998, 'z': -24.0725, 'x': 232.24874999999997}
#move to posB and scan 4 slides
mm.image_pos(posA)

