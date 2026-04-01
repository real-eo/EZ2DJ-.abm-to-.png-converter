class ABMFile:
    # * Offset(h)   Size(h)     Hex                         Description
    #   00          5           41 57 18 00 00              "AW..." (Magic number?)
    #   06          2                                       Image width in px
    #   08          2                                       Image height in px
    #   0A          4           XX XX 00 00 (?)             Unknown                      
    #   0E          4           28 00 00 00                 Unknown
    #   12          1                                       Unknown
    #   13          1                                       Unknown
    #   14          2           00 00                       Unknown                     
    #   16          1                                       Unknown
    #   17          1                                       Unknown 
    #   18          2           00 00                       Unknown                     
    #   1A          2           01 00                       Unknown                     
    #   1C          2                                       Unknown
    #   1E          4           00 00 00 00                 Unknown                     
    #   22          4           XX XX 00 00 (?)             Unknown                     
    #   26          4           XX XX 00 00 (?)             Unknown, same value as Offset(h)=2A   
    #   2A          4           XX XX 00 00 (?)             Unknown, same value as Offset(h)=26   
    #   2E          8           00 00 00 00 00 00 00 00     Header padding?             
    #   36          ... -> EOF  (BB GG RR) (BB GG RR) ...   Pixel data (BGR triplets). NOTE: Files are stored upside-down in BGR, so the first pixel is the bottom-left corner of the image.   
    
    # * Stats:
    #   Total header size: 0x35 (53) bytes
    #   Total data size: (width * height * 3) bytes


    # * Class implementation
    BYTE_ORDER = "little"
    COLOR_MODE = "RGB"                                                                  # 3 bytes per pixel (BGR in this case; not RGB)                     
    COLOR_FORMAT = "BGR"                                                                # Blue, Green, Red

    def __init__(self, filePath):
        # Read the file as bytes
        with open(filePath, "rb") as f:
            self.data = f.read()

        # Parse header
        self.width = int.from_bytes(self.data[6:8], self.BYTE_ORDER)
        self.height = int.from_bytes(self.data[8:10], self.BYTE_ORDER)

        # Parse pixel data
        self.__rawPixelData = self.data[0x36:]
        expectedSize = self.width * self.height * 3
        self.pixelData = self.__rawPixelData[:expectedSize]                             # Ensure correct length


class ABMMask(ABMFile):
    # * Mask files have the same structure as ABM files, but 
    # * with BGR where (FF FF FF) represents 100% transparency 
    # * and (00 00 00) represents 100% opaqueness. The pixel 
    # * data is stored in BGR order, meaning each pixel is 
    # * represented by 3 bytes (Blue, Green, Red). Since this 
    # * is just a mask, the BGR values will be the same for each
    # * pixel. The width and height are still stored in the same 
    # * way as the ABM sprite files, and the pixel data starts
    # * at the same offset (0x36).
    COLOR_MODE = "L"                                                                    # Grayscale (1 byte per pixel)
    COLOR_FORMAT = "L"                                                                  # Grayscale                    

    def __init__(self, filePath, invert=True, normalize=False):
        # * Call the parent constructor to read the file and parse the header
        super().__init__(filePath)

        # * Convert BGR to grayscale (since all channels are the same, we can just take one of them, but ensure to check that they are indeed the same for all pixels)
        gray = self.toGrayscale(self.pixelData)

        # ABM mask uses FF=transparent, 00=opaque, opposite of PNG alpha.
        if invert:  self.maskData = bytes(255 - v for v in gray)
        # While self masking sprites (like combo sprites) use 00=transparent, FF=opaque, same as PNG alpha.
        else:       self.maskData = gray

        if normalize:
            # Normalize the alpha values to the range [0, 255]
            minVal = min(self.maskData)
            maxVal = max(self.maskData)

            if maxVal > minVal:
                self.maskData = bytes((v - minVal) * 255 // (maxVal - minVal) for v in self.maskData)

    @classmethod
    def toGrayscale(cls, bgrData):
        """
        When translating a color image to grayscale (mode "L"),
        the library uses the ITU-R 601-2 luma transform::

            L = R * 299/1000 + G * 587/1000 + B * 114/1000
        """

        return bytes(
            (
                bgrData[i]      * 114   +                                               # Blue pixel data
                bgrData[i + 1]  * 587   +                                               # Green pixel data
                bgrData[i + 2]  * 299                                                   # Red pixel data
            ) // 1000
            for i in range(0, len(bgrData), 3)
        )

