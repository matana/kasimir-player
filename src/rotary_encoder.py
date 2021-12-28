import RPi.GPIO as GPIO


class RotaryEncoder:
    """
    Instantiate the class. Takes two callbacks to run when the
    switch is turned (encoder_on_turn) and pressed (encoder_on_press).
    """

    def __init__(self, callback=None, buttonCallback=None):

        self.lastGpio = None

        self.gpioA = 29  # CLK
        self.gpioB = 31  # DT
        self.gpioButton = 33  # SW

        self.callback = callback
        self.buttonCallback = buttonCallback

        self.levA = 0
        self.levB = 0

        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(self.gpioA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.gpioB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.gpioButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # If event detection(s) are not removed it leads to
        # RuntimeError: Conflicting edge detection already enabled for this GPIO channel
        GPIO.remove_event_detect(self.gpioA)  # <- Fix added when using multiple devices
        GPIO.remove_event_detect(self.gpioB)  # <- Fix added when using multiple devices
        GPIO.remove_event_detect(
            self.gpioButton
        )  # <- Fix added when using multiple devices

        GPIO.add_event_detect(self.gpioA, GPIO.BOTH, self._callback)
        GPIO.add_event_detect(self.gpioB, GPIO.BOTH, self._callback)
        GPIO.add_event_detect(
            self.gpioButton, GPIO.FALLING, self._buttonCallback, bouncetime=500
        )

    def cleanup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.remove_event_detect(self.gpioA)
        GPIO.remove_event_detect(self.gpioB)
        GPIO.remove_event_detect(self.gpioButton)
        GPIO.cleanup()

    def _buttonCallback(self, channel):
        self.buttonCallback(GPIO.input(channel))

    def _callback(self, channel):
        level = GPIO.input(channel)
        if channel == self.gpioA:
            self.levA = level
        else:
            self.levB = level

        # Debounce.
        if channel == self.lastGpio:
            return

        # When both inputs are at 1, we'll fire a callback. If A was the most
        # recent pin set high, it'll be forward, and if B was the most recent pin
        # set high, it'll be reverse.
        self.lastGpio = channel
        if channel == self.gpioA and level == 1:
            if self.levB == 1:
                self.callback(1)
        elif channel == self.gpioB and level == 1:
            if self.levA == 1:
                self.callback(-1)
