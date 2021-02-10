========
Glossary
========

.. glossary::
    :sorted:

    Baud Rate
        The speed of messages sent over a communications bus. It is not
        directly linked but typically infers the interval that messages are
        sent or resent in a protocol.

    C3
        Command, communication, and control board. See
        https://github.com/oresat/oresat-c3

    CAN
        Control area network. A message bus for embedded systems.

    CAN ID
        CAN Identifier. This is the 11-bit CAN message identifier which is at
        the beginning of every CAN message on the bus.

    CANopen
        A communication protocol and device profile specification for a CAN
        bus defined by CAN in Automation. More info at https://can-cia.org/

    CFC
        Cirrus Flux Camera. One of OreSat1 payloads and a Linux board.

    COB ID
        Communication object identifier.

    CubeSat
        A CubeSat is small satellite is made up of multiples of 10cm × 10cm ×
        10cm cubic units

    Daemon
        A long running process on Linux, which runs in the background.

    DLC
        Data Length Code. The operational code dictating the size of the data
        frame.

    EDS
        Electronic Data Sheet. This is an INI style or XML style formatted file.

    NCurses
        New Curses. An application programming interface for manipulating the
        standard terminal. Used for making terminal-based applications without
        the need for a GUI.

    MTU
        Maximum Transmission Unit. The maximum size of a packet. In context of
        this application, the MTU of a CAN packet is 108 bytes for a
        maximum-data-frame size of 64 bits (8 bytes).

    OreSat
        PSAS's open source CubeSat project. See their
        `homepage <https://www.oresat.org/>`_ for more details.

    OreSat0
        A 1U cube-satellite made and maintained by OreSat.

    OreSat1:
        A 2U cube-satellite made and maintained by OreSat.

    OLM
        OreSat Linux Manager. The front end daemon for all OreSat Linux boards.
        It converts CANopen message into DBus messages and vice versa. See
        https://github.com/oresat/oresat-linux-manager

    PDO
        Process Data Object. Inputs and outputs. Values of type rotational
        speed, voltage, frequency, electric current, etc.

    PSAS
        Portland State Aerosapce Society. A student aerospace group at
        Portland State University. See https://www.pdxaerospace.org/

    SDO
        Service Data Object. Configuration settings, possibly node ID, baud
        rate, offset, gain, etc.

    SDR
        Software Define Radio. Radio communications that are traditionally
        implemented in hardware are instead implemented in software.
