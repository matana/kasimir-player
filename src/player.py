#!/usr/bin/python3 -u

from __future__ import annotations
from abc import ABC, abstractmethod
import logging

#############################################################################################
# LOGGER
#############################################################################################
# create logger
logger = logging.getLogger("Kasimir's Player")

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s [%(threadName)s] %(thread)d [%(processName)s] %(process)d"
)

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

#############################################################################################
# SINGLETON
#############################################################################################
import threading


class SingletonMixin(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance


#############################################################################################
# CONTROL ENUM
#############################################################################################

from enum import Enum


class Controller(Enum):
    NEXT = "NEXT"
    PREV = "PREV"


#############################################################################################
# VOLUME
#############################################################################################


class Volume:
    """Holds the volume state and applies changes via `mpc`command."""

    __VOLUME_MIN = 10
    __VOLUME_MAX = 90
    __STEP = 3

    def __init__(self, vol):
        self.vol = vol
        self.__apply(vol)

    def vol_up(self):
        self.vol = (
            self.__VOLUME_MAX
            if self.vol > self.__VOLUME_MAX
            else (self.vol + self.__STEP)
        )
        self.__apply(self.vol)

    def vol_down(self):
        self.vol = (
            self.__VOLUME_MIN
            if self.vol < self.__VOLUME_MIN
            else (self.vol - self.__STEP)
        )
        self.__apply(self.vol)

    def get_vol(self):
        return self.vol

    def __apply(self, vol):
        os.system("mpc vol %s" % vol)

#############################################################################################
# PLAYER
#############################################################################################

import os
from time import sleep
from queue import Queue
from threading import Thread

from playsound import playsound

from read_write_rfid import RFIDWrapper
from rotary_encoder import RotaryEncoder


class Player(SingletonMixin):

    def __init__(self):

        self.__QUEUE = Queue(maxsize=1000)
        """
        Queue (fifo) for messages from callback `encoder_on_turn`.
        see: https://docs.python.org/3/library/queue.html
        """
        self.__VOL = Volume(10)
        self.__THREAD = Thread(target=self.vol_worker, daemon=True).start()
        self.__CURR_PLAYLIST = None
        self.__CONTROLLER = Controller
        self.__READER = RFIDWrapper()
        self.__ENCODER = RotaryEncoder(
            callback=self.encoder_on_turn, buttonCallback=self.encoder_on_press
        )

    def encoder_on_turn(self, delta):
        """The callback (on_turn) receives one argument: a `delta` that will be either 1 or -1.
        One of them means that the dial is being turned to the clockwise; the other
        means that the dial is being turned anticlockwise.
        """
        self.__QUEUE.put(delta)

    def encoder_on_press(self, value):
        os.system("mpc toggle")

    def vol_worker(self):
        """
        worker is started by thread `__THREAD`. Fetches messages from queue. 
        """
        while True:
            self.handle_vol_change(self.__QUEUE.get())
            self.__QUEUE.task_done()

    def handle_vol_change(self, delta):
        if delta == 1:
            self.__VOL.vol_up()
        else:
            self.__VOL.vol_down()
        logger.debug("volume={}".format(self.__VOL.get_vol()))

    def run(self):

        try:
            while True:

                logger.info("hold the card near the rfid reader...")

                code = self.__READER.read_msg_from_card()
                logger.debug("code=%s", code)

                # Retry read in RFID card, if first time was not successful
                if not code:
                    continue

                playsound("beep.wav") # signal for "card has been successfully read out" 

                if code.startswith("playlist"):
                    if (
                        self.__CURR_PLAYLIST is None
                        or self.__CURR_PLAYLIST != code
                    ):
                        logger.info("loading %s ...", code)
                        playlist_id = code.split("playlist:")[1]
                        logger.debug("playlist_id=%s", playlist_id)
                        os.system("mpc clear")
                        os.system("mpc insert spotify:playlist:" + str(playlist_id))
                        os.system("mpc play")
                        self.__CURR_PLAYLIST = code
                    else:
                        logger.debug(
                            "playlist:%s already in use..." % self.__CURR_PLAYLIST
                        )

                if self.__CONTROLLER.NEXT.name == code:
                    os.system("mpc nex")
                    logger.debug("control=%s" % (self.__CONTROLLER.NEXT.name))

                if self.__CONTROLLER.PREV.name == code:
                    os.system("mpc prev")
                    logger.debug("control=%s" % (self.__CONTROLLER.PREV.name))

                sleep(0.5)  # pause main thread for 0.5 sec

        except (KeyboardInterrupt, Exception) as e:
            raise e
        finally:
            self.__READER.cleanup()
            self.__ENCODER.cleanup()


if __name__ == "__main__":
    player = Player().instance()
    player.run()
