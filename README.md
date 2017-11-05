#RESTwise
##A REST web interface for plugwise meters.

This project is work in progress.

## Command reference

### Some things I noticed
Command response code nearly always seems to be the command code +1.
Every so often a stray \x83 character is injected into the receive stream. No idea what this means (heartbeat?)

Invalid command codes are acknowledged OK, but return an response message like the following:
```
Send    \x05\x05\x03\x03AA77E803\r\n
Receive \x05\x05\x03\x030000000900C1FCC0\r\n
Receive \x05\x05\x03\x030000000900E15666\r\n
```

The 00E1 probably means command not recognized.

### Ack message
Acknowledge messages are always received after sending a command, right before the actual command response.

Example:
```
Send    \x05\x05\x03\x030008014068\r\n
Receive \x05\x05\x03\x030000017E00C11A4D\r\n
```

Response data:
|Type|Description|Data in example|
|--|--|--|
|Uint16|Response 'command' code', always 0000|0000|
|Uint16|Sequence number. This number will be used in the actual command response and increments after each command.|017E|
|Uint16|Status code|00C1|

|Status code|Description|
|--|--|
|00C1|Command received successfully. <br />This does NOT mean the command itself was successful, for this the actual command response must be used.|
|00C2|CRC error, the command checksum is not ok|

###Command 0x0008
Description: Unknown (get Circle+ MAC?)
Payload data:
|Type|Description|Data in example|
|--|--|--|
|Uint8|A byte (bool?)|01|

Example:
Byte field is 1
```
Send    \x05\x05\x03\x030008014068\r\n
Receive \x05\x05\x03\x030000017E00C11A4D\r\n
Receive \x05\x05\x03\x030000017E00D9000D6F0001A5A3729865\r\n
```
Or
Byte field is 0
```
Send    \x05\x05\x03\x030008005049\r\n
Receive \x05\x05\x03\x03000000EA00C1E5F6\r\n
Receive \x05\x05\x03\x03000000EA00DD000D6F0001A5A372CDA9\r\n
```

Response data:
|Type|Description|Data in example|
|--|--|--|
|Uint16|Command response code|0000|
|Uint16|Sequence number|017E|
|Uint16|Unknown|00D9|
|Uint64|Circle+ MAC|000D6F0001A5A372|

###Command 0x000A (from plugwise unleashed)
Description: Init/Reset the stick
No data

Example:
```
Send     \x05\x05\x03\x03000AB43C\r\n
Receive  \x05\x05\x03\x03000000E700C135F5\r\n
Receive  \x05\x05\x03\x03001100E7000D6F0001A59EDC0101FD0D6F0001A5A37234FDFF9418\r\n
Receive  \x83
```

Response data:
|Type|Description|Data in example|
|--|--|--|
|Uint16|Command response code|0011|
|Uint16|Sequence number|00E7|
|Uint64|MAC of stick|000D6F0001A59EDC|
|Uint8|Unknown, usually 01|01|
|Uint8|Link up.<br/>1 if associated with circle+, 0 otherwise|01|
|Uint64|Long network code|FD0D6F0001A5A372|
|Uint16|Short network code|34FD|
|Uint8|Unknown, always 0xFF|FF|

###Command 0x0012
Description: Unknown

Example:
```
Send    \x05\x05\x03\x030012000D6F0001A20F97AFC7\r\n
Receive \x05\x05\x03\x03000000F200C1D842\r\n
Receive \x05\x05\x03\x03001300F2000D6F0001A20F97000200140000245700000000000FED46\r\n
```

###Command 0x0016
Description: Unknown

Example:
```
Send    \x05\x05\x03\x030016000D6F0001A5A372110B091FFFFFFFFF0E373B04C056\r\n
Receive \x05\x05\x03\x030000017000C1249C\r\n
Receive \x05\x05\x03\x030000017000D7000D6F0001A5A3725774\r\n
```

###Command 0x0018
Description: Unknown

Example:
```
Send    \x05\x05\x03\x030018000D6F0001A5A37200C50F\r\n
Receive \x05\x05\x03\x030000012E00C1594C\r\n
Receive \x05\x05\x03\x030019012E000D6F0001A5A372000D6F0001A400E2006B33\r\n
```

###Command 0x0023
Description: Device information request
Payload data:
|Type|Description|Data in example|
|--|--|--|
|Uint64|MAC of unit to receive info from|000D6F0001A59EDC|

Example:
```
Send    \x05\x05\x03\x030023000D6F0001A59EDC32B2\r\n
Receive \x05\x05\x03\x030000016E00C15FED\r\n
Receive \x05\x05\x03\x030024016E000D6F0001A59EDC000000000000000000806539070085114E0842BB0067A1\r\n
```

###Command 0x0026 (from plugwise unleashed)
Description: Retrieve circle(+) calibration data
Payload data:
|Type|Description|Data in example|
|--|--|--|
|Uint64|MAC of unit to get calibration data from|000D6F0001A400E2|

Example:
```
Send    \x05\x05\x03\x030026000D6F0001A400E25681\r\n
Receive \x05\x05\x03\x03000000F400C115C7\r\n
Receive \x83
Receive \x05\x05\x03\x03002700F4000D6F0001A400E23F7F1C61B60D16843D2822C100000000BF7F\r\n
```

Response data:
|Type|Description|Data in example|
|--|--|--|
|Uint16|Command response code|0027|
|Uint16|Sequence number|00F4|
|Uint64|MAC of device being calibrated|000D6F0001A400E2|
|Real32|Calibration gain A|3F7F1C61|
|Real32|Calibration gain B|B60D1684|
|Real32|Calibration offset|3D2822C1|
|Real32|Offset noise|00000000|

###Command 0x0028
Description: Unknown

Example
```
Send    \x05\x05\x03\x030028000D6F0001A5A372005614040211178BC6\r\n
Receive \x05\x05\x03\x030000017200C1601F\r\n
Receive \x05\x05\x03\x030000017200DF000D6F0001A5A372A65C\r\n
```

###Command 0x0029
Description: Unknown (Circle+ build info?)
Payload data:
|Type|Description|Data in example|
|--|--|--|
|Uint64|Circle+ MAC|000D6F0001A5A372|

Example:
```
Send    \x05\x05\x03\x030029000D6F0001A5A3720AC4\r\n
Receive \x05\x05\x03\x03000000EB00C10B24\r\n
Receive \x05\x05\x03\x03003A00EB000D6F0001A5A3725753140402111710A2\r\n
```

Response data (assuming build info):
|Type|Description|Data in example|
|--|--|--|
|Uint16|Command response code|003A|
|Uint16|Sequence number|00F4|
|Uint64|Circle+ MAC|000D6F0001A5A372|
|Uint16|Build number?|5753|
|Date|Build date (YYMMDDHHMM)?|1404021117|

###Command 0x003E
Description: Unknown
Payload data:
|Type|Description|Data in example|
|--|--|--|
|Uint64|Endpoint MAC address|000D6F0001A40223|

Example:
```
Send    \x05\x05\x03\x03003E000D6F0001A40223221E\r\n
Receive \x05\x05\x03\x03000000FE00C1A210\r\n
Receive \x05\x05\x03\x03003F00FE000D6F0001A402230E36040401457ABADC\r\n
```

Response data (wild guess):
|Type|Description|Data in example|
|--|--|--|
|Uint16|Command response code|003F|
|Uint16|Sequence number|00FE|
|Uint64|Endpoint MAC|000D6F0001A40223|
|????|Unknown|0E36040401457A|

###Command 0x0040
Description: Unknown

Example:
```
Send    \x05\x05\x03\x030040000D6F0001A402230001738B\r\n
Receive \x05\x05\x03\x03000000FF00C14CC2\r\n
Receive \x05\x05\x03\x03000000FF00E5000D6F0001A402238EE1\r\n
```

###Command 0x004A
Description: Unknown

Example:
```
Send    \x05\x05\x03\x03004A000D6F0001A5A3723C016934\r\n
Receive \x05\x05\x03\x030000017300C1CA4E\r\n
Receive \x83'
Receive \x05\x05\x03\x030000017300F1000D6F0001A5A372AB40\r\n
```

###Command 0x0058
Description: Unknown

Example:
```
Send    \x05\x05\x03\x030058000D6F0001A20F97007DC0\r\n
Receive \x05\x05\x03\x030000019200C1E0BC\r\n
Receive \x05\x05\x03\x030000019200F9000D6F0001A20F97C8B3\r\n
```

###Command 0x005F
Description: Unknown

Example:
```
Send    \x05\x05\x03\x03005F000D6F0001A400E2FC53\r\n
Receive \x05\x05\x03\x03000000F500C1BF96\r\n
Receive \x05\x05\x03\x03006000F5000D6F0001A400E2FFFFFFFFFFFFFFFE3E91\r\n
```

