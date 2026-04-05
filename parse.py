class ABMFile:
    # * Offset(h)   Size(h)     Hex                         Description
    #   00          2           41 57                       Magic number ("AW") 
    #   02          4                                       Bytes per pixel. NOTE: Normally 24 (3 bytes per pixel, BGR), but some files use 32 (4 bytes per pixel, BGRA) and 16 (2 bytes per pixel, probably BGR565) 
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
    COLOR_MODE = ...                 
 
    def __init__(self, filePath):
        # Read the file as bytes
        with open(filePath, "rb") as f:
            self.data = f.read()

        # Parse header
        self.bitsPerPixel = int.from_bytes(self.data[2:6], self.BYTE_ORDER)
        self.width = int.from_bytes(self.data[6:8], self.BYTE_ORDER)
        self.height = int.from_bytes(self.data[8:10], self.BYTE_ORDER)

        # Parse pixel data
        self.__rawPixelData = self.data[0x36:]
        expectedSize = self.width * self.height * (self.bitsPerPixel // 8)              # Calculate expected size based on width, height, and bits per pixel
        self.pixelData = self.__rawPixelData[:expectedSize]                             # Ensure correct length

        # Format-specific processing based on bits per pixel
        match self.bitsPerPixel:
            # 16 bits: BGR565 
            case 0x10:
                self.COLOR_MODE = "RGB"                                                 
                self.COLOR_FORMAT = "BGR565"                                            # BGR565 (5 bits for Blue, 6 bits for Green, 5 bits for Red)
            
            # 24 bits: BGR
            case 0x18:                                                                  
                self.COLOR_MODE = "RGB"
                self.COLOR_FORMAT = "BGR"                                               # Blue, Green, Red

            # 32 bits: BGRA
            case 0x20:
                self.COLOR_MODE = "RGBA"
                self.COLOR_FORMAT = "BGRA"                                              # Blue, Green, Red, Alpha

                self.mask = ABMMask.from32bitABM(self)                                  # Extract alpha mask from 32-bit ABM file
                self.pixelData = bytes(                                                 # Nuke the alpha bytes
                    self.pixelData[i] if i % 4 != 3 else 255 for i in range(len(self.pixelData))
                )
            
            # Unsupported bits per pixel
            case _:
                raise ValueError(f"Unsupported bits per pixel: {self.bitsPerPixel}")
        
        # Check if the pixel data is shorter than expected
        if len(self.pixelData) < expectedSize:
            print(f"Warning: Expected pixel data size {expectedSize} bytes, but got {len(self.pixelData)} bytes. The image may be incomplete or corrupted.")

            # Pad with zeros
            self.pixelData += bytes(expectedSize - len(self.pixelData))
            self.padded = True
        else:
            self.padded = False


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

        # Normalize the alpha values to the range [0, 255] if requested
        if normalize:
            self.maskData = self.normalize(self.maskData)


    @classmethod
    def from32bitABM(cls, abmFile: ABMFile, invert=True, normalize=False):
        """
        Create an ABMMask instance from a 32-bit ABM file by extracting the alpha channel.
        The alpha channel is the 4th byte of each pixel in the pixel data. 
        The method will read the pixel data, extract the alpha values, 
        and create a new ABMMask instance with the extracted mask data.
        """

        if abmFile.COLOR_MODE != "RGBA":
            raise ValueError("ABM file must be 32 bits per pixel (BGRA) to extract alpha mask")

        # Extract alpha channel (4th byte of each pixel)
        alpha = bytes(abmFile.pixelData[i + 3] for i in range(0, len(abmFile.pixelData), 4))

        # ABM mask uses FF=transparent, 00=opaque, opposite of PNG alpha.
        if invert:      maskData = bytes(255 - v for v in alpha)
        # While self masking sprites (like combo sprites) use 00=transparent, FF=opaque, same as PNG alpha.
        else:           maskData = alpha

        # Normalize the alpha values to the range [0, 255] if requested
        if normalize:   maskData = cls.normalize(maskData)

        # Create an ABMMask instance with the extracted mask data
        mask = cls.__new__(cls)                                                         # Create an uninitialized instance
        
        mask.width = abmFile.width
        mask.height = abmFile.height
        mask.COLOR_MODE = "L"
        mask.COLOR_FORMAT = "L"
        mask.maskData = maskData

        return mask

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
    
    @classmethod
    def normalize(data):
        # Normalize the alpha values to the range [0, 255]
        minVal = min(data)
        maxVal = max(data)

        if maxVal > minVal:
            return bytes((v - minVal) * 255 // (maxVal - minVal) for v in data)


