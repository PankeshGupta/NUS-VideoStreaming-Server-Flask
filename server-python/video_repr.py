class VideoRepresentation(object):
    def __init__(self, name, bandwidth, width, height):
        self.name = name
        self.bandwidth = bandwidth
        self.width = width
        self.height = height

    def __composite_values__(self):
        return self.name, self.bandwidth, self.width, self.height

    def __repr__(self):
        return "Representation(bandwidth=%r, width=%r, height=%r)" % (self.bandwidth, self.width, self.height)

    def __eq__(self, other):
        return isinstance(other, VideoRepresentation) and \
               other.name == self.name and \
               other.bandwidth == self.bandwidth and \
               other.width == self.width and \
               other.height == self.height

    def __ne__(self, other):
        return not self.__eq__(other)


class DefaultRepresentations(object):
    HIGH = VideoRepresentation(
        name='HIGH',
        bandwidth=3000000,
        width=720,
        height=480
    )

    MEDIUM = VideoRepresentation(
        name='MEDIUM',
        bandwidth=768000,
        width=480,
        height=320
    )

    LOW = VideoRepresentation(
        name='LOW',
        bandwidth=200000,
        width=240,
        height=160
    )
