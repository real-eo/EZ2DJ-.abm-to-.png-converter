from pathlib import Path


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
    #   36          ...         (BB GG RR) (BB GG RR) ...   Pixel data (BGR triplets). NOTE: Files are stored upside-down in BGR, so the first pixel is the bottom-left corner of the image.   
    #   EOF-02      2                                       Unknown, often 00 00
    
    # * Stats:
    #   Total header size: 0x35 (53) bytes
    #   Total data size: (width * height * (bitsPerPixel // 8)) bytes

    # * Catcher headers
    #  bar0000.abm      (Catcher1): 41 57 18 00 00 00 40 00 40 00 AC 10 00 00 28 00 00 00 E1 CF 00 00 EE 51 00 00 01 00 97 B1 00 00 00 00 02 30 00 00 12 0B 00 00 12 0B 00 00 00 00 00 00 00 00 00 00 
    # 2bar0000.abm      (Catcher2): 41 57 18 00 00 00 40 00 40 00 AC 10 00 00 28 00 00 00 E1 CF 00 00 EE 51 00 00 01 00 97 B1 00 00 00 00 02 30 00 00 12 0B 00 00 12 0B 00 00 00 00 00 00 00 00 00 00
    # 3bar0000.abm      (Catcher3): 41 57 10 00 00 00 40 00 40 00 AC 10 00 00 28 00 00 00 E1 CF 00 00 EE 51 00 00 01 00 9F B1 00 00 00 00 02 20 00 00 60 0F 00 00 60 0F 00 00 00 00 00 00 00 00 00 00
    # 4bar0000.abm      (Catcher4): 41 57 20 00 00 00 5A 00 3C 00 AC 10 00 00 28 00 00 00 FB CF 00 00 92 51 00 00 01 00 AF B1 00 00 00 00 62 54 00 00 60 0F 00 00 60 0F 00 00 00 00 00 00 00 00 00 00
    # hero0000.abm      (Catcher5): 41 57 10 00 00 00 40 00 40 00 AC 10 00 00 28 00 00 00 E1 CF 00 00 EE 51 00 00 01 00 9F B1 00 00 00 00 02 20 00 00 60 0F 00 00 60 0F 00 00 00 00 00 00 00 00 00 00
    # princess0000.abm  (Catcher6): 41 57 10 00 00 00 40 00 40 00 AC 10 00 00 28 00 00 00 E1 CF 00 00 EE 51 00 00 01 00 9F B1 00 00 00 00 02 20 00 00 60 0F 00 00 60 0F 00 00 00 00 00 00 00 00 00 00
    # smin_0001.abm     (Catcher7): 41 57 18 00 00 00 5A 00 3C 00 AC 10 00 00 28 00 00 00 FB CF 00 00 92 51 00 00 01 00 97 B1 00 00 00 00 C0 3F 00 00 13 0B 00 00 13 0B 00 00 00 00 00 00 00 00 00 00



    # * Class implementation
    BYTE_ORDER = "little"
    COLOR_MODE = "RGB"
    COLOR_FORMAT = "BGR"                                                                # Blue, Green, Red              


    def __init__(self, filePath: (Path | str)):
        # Convert to Path object if not already
        self.path = Path(filePath) if not isinstance(filePath, Path) else filePath

        # Read the file as bytes
        with open(self.path, "rb") as f:
            self.data = f.read()

        # Parse header
        self.bitsPerPixel = int.from_bytes(self.data[0x02:0x06], self.BYTE_ORDER)
        self.width = int.from_bytes(self.data[0x06:0x08], self.BYTE_ORDER)
        self.height = int.from_bytes(self.data[0x08:0x0A], self.BYTE_ORDER)

        # Parse pixel data
        self.__strided = self.data[0x36:]                                               # ? Rows padded to alignment boundary (what's on disk)
        self.__packed = bytearray()                                                     # ? Rows tightly back-to-back with no padding (what Pillow expects)                      

        bytesPerPixel = self.bitsPerPixel // 8
        bytesPerRow = self.width * bytesPerPixel                                        # Calculate the number of bytes per row based on the image width and bytes per pixel
        stridedRowSize = ((bytesPerRow + 3) // 4) * 4                                   # Rows are padded to the next multiple of 4 bytes

        # ? Unsure if this is correct
        # ? payloadSize26 = int.from_bytes(self.data[0x26:0x2A], self.BYTE_ORDER)
        # ? payloadSize2a = int.from_bytes(self.data[0x2A:0x2E], self.BYTE_ORDER)
        # ? print(payloadSize26, payloadSize2a)


        # Strip padding
        self.padded = False                                                             # Flag to indicate if any rows were padded 

        # ? The loop reads strided chunks of `stridedRowSize` sized bytes from `self.__strided`, 
        # ? and only keeps the first `bytesPerRow` of each, building up the packed result.
        for y in range(self.height): 
            start = y * stridedRowSize
            end = start + bytesPerRow
            row = self.__strided[start:end]

            # Check if the pixel data for the current row is shorter than expected
            if len(row) < bytesPerRow:
                print(f" Warning! The required amount of raw pixel data per row required " + 
                                f"is {bytesPerRow} bytes, but got {len(row)} bytes for " + 
                                f"row {y}. The image may be incomplete or corrupted.")
                
                # Pad with zeros
                row = row + bytes(bytesPerRow - len(row))
                self.padded = True

            self.__packed.extend(row)                                                   # Append the stripped row to the packed pixel data

        self.pixelData = bytes(self.__packed)                                           # Final packed pixel data with padding stripped
   

        # Format-specific processing based on bits per pixel
        match self.bitsPerPixel:
            # 16 bits: RGB555 
            case 0x10:                
                # // self.COLOR_MODE = "RGB"
                # // self.COLOR_FORMAT = "BGR"                                               # Blue, Green, Red         
                self.pixelData = self.RGB555toBGR888(self.pixelData)                    # RGB555 (5 bits for Red, 5 bits for Green, 5 bits for Blue)
            
            # 24 bits: BGR
            case 0x18:
                # // self.COLOR_MODE = "RGB"
                # // self.COLOR_FORMAT = "BGR"                                               # Blue, Green, Red                                                                  
                pass

            # 32 bits: BGRA
            case 0x20:
                # // self.COLOR_MODE = "RGBA"
                # // self.COLOR_FORMAT = "BGRA"                                              # Blue, Green, Red, Alpha

                self.alphaChannel = ABMMask.from32bitABM(self)                          # Extract alpha mask from 32-bit ABM file
                self.pixelData = bytes(                                                 # Nuke the alpha channel from the pixel data
                    self.pixelData[i]
                    for i in range(len(self.pixelData))
                    if i % 4 != 3
                )
            
            # Unsupported bits per pixel
            case _:
                raise ValueError(f"Unsupported bits per pixel: {self.bitsPerPixel}")

            

    @staticmethod
    def RGB555toBGR888(data):
        """Convert little-endian RGB555/XRGB1555 words to packed BGR888 bytes."""
        out = bytearray()

        for i in range(0, len(data) - 1, 2):
            value = data[i] | (data[i + 1] << 8)

            # Stored on disk as little-endian bytes (low byte first)
            # Bit layout: [X][RRRRR][GGGGG][BBBBB]  (MSB->LSB)
            red5 = (value >> 10) & 0x1F
            green5 = (value >> 5) & 0x1F
            blue5 = value & 0x1F

            red8 = (red5 << 3) | (red5 >> 2)
            green8 = (green5 << 3) | (green5 >> 2)
            blue8 = (blue5 << 3) | (blue5 >> 2)

            out.extend((blue8, green8, red8))  # BGR for Pillow raw decoder

        return bytes(out)
 


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

    def __init__(self, filePath: (Path | str), invert=True, normalize=False):
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

        if abmFile.bitsPerPixel != 0x20:
            raise ValueError(f"({abmFile.path}) ABM file must be 32 bits per pixel (BGRA) to extract alpha mask")

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
    
    @staticmethod
    def normalize(data):
        # Normalize the alpha values to the range [0, 255]
        minVal = min(data)
        maxVal = max(data)

        if maxVal > minVal:
            return bytes((v - minVal) * 255 // (maxVal - minVal) for v in data)


