#!/usr/bin/env python

import RPi.GPIO as GPIO
from pi_rc522.pirc522 import RFID


class RFIDWrapper(object):
    """Extends the base class from source repository by two additional functions:
    `write_msg_to_card()` and `read_msg_from_card()`.

    Project repository: https://github.com/ondryaso/pi-rc522  \n
    Cheetsheet MIFARE (RFID RC522 module): https://www.nxp.com/docs/en/data-sheet/MF1S50YYX_V1.pdf
    """

    BLOCK_ADDRS = [8, 9, 10]
    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]  # deafult auth key
    write = True

    def __init__(self):
        self.rdr = RFID()
        self.rdr.set_antenna_gain(5)  # default is 4
        self.util = self.rdr.util()
        self.util.debug = True

    def write_msg_to_card(self):
        """Utility function for storing information on RFID cards in predefined data blocks `[8,9,10]`.

        Currently the max character length
        is set to 48 (3 blocks a 16 bytes), but can be extended easily by adding more data block adresses to attribute `BLOCK_ADDRS`
        """

        msg = input(
            "Please enter the `msg` you would like to store on the RFID card and press [enter]...\n>"
        )

        if len(self.BLOCK_ADDRS) * 16 < len(msg):
            raise ValueError(
                "msg (len=%s) has more characters then resereved block/bytes (len=%s) "
                % ((len(self.BLOCK_ADDRS) * 16), len(msg))
            )

        while self.write:
            print("\nHold RFID card near scanner")
            self.rdr.wait_for_tag()

            (error, data) = self.rdr.request()
            if not error:
                print("\nDetected: " + format(data, "02x"))

            (error, uid) = self.rdr.anticoll()
            if not error:
                print("\nCard read UID:%s" % uid)

                print("\nSetting tag")
                self.util.set_tag(uid)

                print("\nAuthorizing")
                self.util.auth(self.rdr.auth_a, self.key)

                print("\nWriting bytes...")
                data = bytearray()
                # Adjust 'msg' length from input to fit into reserved blocks 'BLOCK_ADDRS' (len([8, 9, 10])*16 charcters).
                data.extend(
                    bytearray(msg.ljust(len(self.BLOCK_ADDRS) * 16).encode("ascii"))
                )
                i = 0
                for block_num in self.BLOCK_ADDRS:
                    # `self.util.rewrite` overrides the data at the specified block adress with the given data (each chunk has a length of 16 bytes)
                    error = self.util.rewrite(block_num, data[(i * 16) : (i + 1) * 16])
                    if not error:
                        print("\nDone writing block_num #%s" % block_num)
                    if self.util.debug:
                        print(
                            "Adress:%s, data:%s"
                            % (block_num, data[(i * 16) : (i + 1) * 16])
                        )
                    i += 1

                # Code in debug can be used to read out (msg) data form rfid card
                data = []
                to_txt = ""
                for block_num in self.BLOCK_ADDRS:
                    # before reading data from rfid card, we have to authenticate with the given block adress
                    error = self.rdr.card_auth(
                        self.rdr.auth_a, block_num, self.key, uid
                    )
                    if not error:
                        # read the bytes (array, again if fixed lenght 16) from block adress
                        (error, back_data) = self.rdr.read(block_num)
                        if self.util.debug:
                            print(
                                "\nReading block %s: %s"
                                % (block_num, str((error, back_data)))
                            )
                        # append each 16 byte array block form every data adress block into `data`
                        data += back_data
                # always stop crypto1 when done working, as proposed in pirc522 source repo
                self.rdr.stop_crypto()
                if data:
                    # text representation with simple byte to char conversion
                    to_txt = "".join(chr(i) for i in data)
                    if self.util.debug:
                        print("\nData read form card:" + to_txt)

                if to_txt.strip() == msg:
                    self.write = False
                else:
                    raise Exception(
                        "The `msg` was not written completely to card! Please retry."
                    )

                print("\nDeauthorizing")
                self.util.deauth()

        print("Done :)")

    def read_msg_from_card(self):
        """Utility function for reading out information from RFID cards from reserved data blocks `[8,9,10]`."""
        self.rdr.wait_for_tag()

        (error, data) = self.rdr.request()
        if not error:
            print("\nDetected: " + format(data, "02x"))

        (error, uid) = self.rdr.anticoll()
        if not error:
            print("\nCard read UID:%s" % uid)
            # Select Tag is required before Auth
            if not self.rdr.select_tag(uid):
                data = []
                to_txt = ""
                for block_num in self.BLOCK_ADDRS:
                    # before reading data from rfid card, we have to authenticate with the given block adress
                    error = self.rdr.card_auth(
                        self.rdr.auth_a, block_num, self.key, uid
                    )
                    if not error:
                        # read the bytes (array, again if fixed lenght 16) from block adress
                        (error, back_data) = self.rdr.read(block_num)
                        if self.util.debug:
                            print(
                                "\nReading block %s: %s"
                                % (block_num, str((error, back_data)))
                            )
                        # append each 16 byte array block form every data adress block into `data`
                        data += back_data
                # always stop crypto1 when done working, as proposed in pirc522 source repo
                self.rdr.stop_crypto()
                if data:
                    # text representation with simple byte to char conversion
                    to_txt = "".join(chr(i) for i in data)
                    if self.util.debug:
                        print("\nData read form card:" + to_txt)
                    return to_txt.strip()

    def cleanup(self):
        self.rdr.cleanup()

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Read or Write information from/to RFID card depending on the mode. An argument [-w | -r] flag ist mandatory. \nScript ma be called either in --write or --read mode."
    )
    parser.add_argument("-w", "--write", action="store_true")
    parser.add_argument("-r", "--read", action="store_true")
    args = parser.parse_args()

    if args.write and args.read:
        raise ValueError("Either --write or --read mode may be called")

    try:
        wrapper = RFIDWrapper()
        if args.write:
            wrapper.write_msg_to_card()
        elif args.read:
            print("Read mode selected, hold card near scanner...")
            while True:
                txt = wrapper.read_msg_from_card()
                print("Result=%s" % txt)
        else:
            parser.print_help()
    except (KeyboardInterrupt, Exception) as e:
        print("Either KeyboardInterrupt or Exception was raised: %s " % e)
        raise e
    finally:
        wrapper.cleanup()
