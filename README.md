# CANcli

A utility for displaying and tracking activity over the CAN bus.

#### Usage

  * `$` `./cancli [interfaces]`

##### Ex:

  * `$` `./cancli can0`

##### Node ID Ranges:

  * **Hearbeat:** `0x701 - 0x7FF`
  * **PDO:** `0x181 - 0x57F`
  * **SDO:**
    * _tx:_ `0x581 - 0x5FF`
    * _rx:_ `0x601 - 0x67F`
