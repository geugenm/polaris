#
# Preprocessor used in kaitai struct to remove the escape sequences of
# an ELFIN STAR telemetry frame
#
# Patrick Dohmen, DL4PD (dl4pd@darc.de)
# With the kind help of Mikhail Yakshin
#
# Usage in 'kaitai struct':
#
# types:
#   preprocessor:
#     seq:
#       - id: databuf
#         process: elfin_pp
#         size-eos: true
#

import binascii

class ElfinPp:
    def decode(self, bindata):
        i = 0
        binlen = len(bindata)
        out = bytearray(b'')
        while i < binlen:
            ch = bindata[i]
            if ch == 0x27 and i + 1 < binlen:
                next_ch = bindata[i + 1]
                if next_ch == 0x27 or next_ch == 0x5e or next_ch == 0x9e:
                    i += 1
            out.append(bindata[i])
            i += 1
        return out
