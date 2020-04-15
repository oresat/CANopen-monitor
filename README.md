# CANopen-monitor

A utility for displaying and tracking activity over the CAN bus.

### Installation

  __(Manual) Git Installation:__

  Clone the repo:

  `$` `git clone https://github.com/oresat/CANopen-monitor.git`

  Run the local start script:

  `$` `./CANopen-monitor/can-monitor`

***

### Usage

  Start can-monitor tool:
  * `$` `can-monitor`

***

### Configs:

  The config files are by default stored in `~/.canmon`

#### Defaults:
###### `~/.canmon/devices.json`
```json
[
  "can0"
]
```

&nbsp;

###### `~/.canmon/tables.json`
```json
[{
  "name": "Hearbeats",
  "capacity": 16,
  "stale_node_timeout": 60,
  "dead_node_timeout": 600
},
{
  "name": "Misc",
  "capacity": 64,
  "stale_node_timeout": null,
  "dead_node_timeout": null
}]
```

***

### Node IDs/Frame Types:

###### [Wikipedia Table](https://en.wikipedia.org/wiki/CANopen#Predefined_Connection_Set.5B7.5D)

###### Abridged Table:

  * **Hearbeat:** `0x701 - 0x7FF`
  * **PDO:** `0x181 - 0x57F`
  * **SDO:**
    * _tx:_ `0x581 - 0x5FF`
    * _rx:_ `0x601 - 0x67F`
