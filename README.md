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
|00E1|Communication failure, endpoint was probably not found.<br/>This status code always follows as a second ack to the command!|


---
###Command 0x0007
Description: Associate endpoint (connect to device)

Payload data:

|Type|Description|Data in example|
|--|--|--|
|Uint8|A byte (bool?)|01|
|Uint64|Endpoint MAC|000D6F00DEADBEEF|


Example:
```
Send    \x05\x05\x03\x03000701000D6F00DEADBEEFFF58\r\n'
Receive \x05\x05\x03\x03000000B500C1B937\r\n'
```

Oddly enough there is no actual command response to this command. Command 00x23 is used to poll the status of the endpoint.


---
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
|Uint16|Unknown|00D9/00DD|
|Uint64|Circle+ MAC|000D6F0001A5A372|


---
###Command 0x0009
Description: Disassociate endpoint?

Payload data:
|Type|Description|Data in example|
|--|--|--|
|Uint64|Endpoint MAC|000D6F0001A400E2|
|Uint16|No idea, could also be 2 Uint8 fields|0204|

In the experiment I did command 0x009 was always followed up by command 0x001C.

Example:
```
Send    \x05\x05\x03\x030009000D6F0001A400E20204B7E0\r\n
Receive \x05\x05\x03\x03000000BD00C10EE0\r\n
Receive \x05\x05\x03\x03000000BD00F2000D6F0001A400E20F3E\r\n
```

Response data:

|Type|Description|Data in example|
|--|--|--|
|Uint16|Command response code|0000|
|Uint16|Sequence number|00BD|
|Uint16|Unknown, seems to stay 00F2|00F2|
|Uint64|Endpoint MAC|000D6F0001A400E2|


---
###Command 0x000A (from plugwise unleashed)
Description: Init/Reset the stick

No data

Example:
```
Send     \x05\x05\x03\x03000AB43C\r\n
Receive  \x05\x05\x03\x03000000E700C135F5\r\n
Receive  \x05\x05\x03\x03001100E7000D6F0001A59EDC0101FD0D6F0001A5A37234FDFF9418\r\n
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


---
###Command 0x0012 (from plugwise unleashed)
Description: Power information request (current power usage measurement)

Payload data:

|Type|Description|Data in example|
|--|--|--|
|Uint64|Endpoint MAC|000D6F0001A20F97|

Example:
```
Send    \x05\x05\x03\x030012000D6F0001A20F97AFC7\r\n
Receive \x05\x05\x03\x03000000F200C1D842\r\n
Receive \x05\x05\x03\x03001300F2000D6F0001A20F97000200140000245700000000000FED46\r\n
```

Response data:

|Type|Description|Data in example|
|--|--|--|
|Uint16|Command response code|0013|
|Uint16|Sequence number|00F2|
|Uint64|Endpoint MAC|000D6F0001A20F97|
|Uint16|Pulses per 1 second interval|0002|
|Uint16|Pulses per 8 second interval|0014|
|Uint32|Total number of pulses (consumption?)|00002457|
|Uint32|Total number of pulses (production)|00000000|
|Uint16|Unknown|000F|

Example conversion code (credits Maarten Damen)
```python
def pulsecorrection(pulses, timespansource, timespantarget, gain_a, gain_b, offtot, offnoise):
    """
    Corrects pulses based on calibration information, and time elapsed.
    """
    if pulses == 0.0:
        return 0.0

    corrected = 0.0
    value = pulses / timespansource
    value += offnoise
    out = timespantarget * (((pow(value, 2.0) * gain_b) + (value * gain_a)) + offtot)
    return out

def pulsetowatt(pulses):
    """
    Converts pulses to the watt unit.
    """
    return(self.pulsetokwh(pulses) * 1000) 

def pulsetokwh(pulses):
    """
    Converts pulses to the kWh unit.
    """
    return (pulses / 3600.0) / 468.9385193
```

---
###Command 0x0016
Description: Unknown

Payload data:

|Type|Description|Data in example|
|--|--|--|
|Uint64|Circle+ MAC address|000D6F0001A5A372|
|???|Unknown|110B091FFFFFFFFF0E373B04|

Example:
```
Send    \x05\x05\x03\x030016000D6F0001A5A372110B091FFFFFFFFF0E373B04C056\r\n
Receive \x05\x05\x03\x030000017000C1249C\r\n
Receive \x05\x05\x03\x030000017000D7000D6F0001A5A3725774\r\n
```
Response data:

|Type|Description|Data in example|
|--|--|--|
|Uint16|Unknown|00D7|
|Uint64|Circle+ MAC|000D6F0001A5A372|


---
###Command 0x0018
Description: Get endpoint MAC

Payload data:

|Type|Description|Data in example|
|--|--|--|
|Uint64|Circle+ MAC address|000D6F0001A5A372|
|Uint8|Index of the endpoint to get the MAC for (0 based)|00|

In total 63 (0x3F) endpoints can be assigned.

Example:
```
Send    \x05\x05\x03\x030018000D6F0001A5A37200C50F\r\n
Receive \x05\x05\x03\x030000012E00C1594C\r\n
Receive \x05\x05\x03\x030019012E000D6F0001A5A372000D6F0001A400E2006B33\r\n
```
Or, when the index is unassigned:
```
Send    \x05\x05\x03\x030018000D6F0001A5A3721BA8EB\r\n
Receive \x05\x05\x03\x030000014900C14200\r\n
Receive \x05\x05\x03\x0300190149000D6F0001A5A372FFFFFFFFFFFFFFFF1B0918\r\n
```

Response data

|Type|Description|Data in example|
|--|--|--|
|Uint16|Command response code|0019|
|Uint16|Sequence number|012E|
|Uint64|Circle+ MAC this unit is associated to|000D6F0001A5A372|
|Uint64|Requested endpoint MAC|000D6F0001A400E2/FFFFFFFFFFFFFFFF|
|Uint8|Endpoint index (0 based)|00/1B|


---
###Command 0x001C
Description: Remove endpoint from Circle+/Stick registered nodes list.

Payload data:

|Type|Description|Data in example|
|--|--|--|
|Uint64|Circle+ MAC|000D6F0001A5A372|
|Uint64|MAC of endpoint to remove|000D6F0001A404A5|

In the experiment I did this command was always preceded by command 0x009, but only if the node being removed existed/was online.

Example:
```
Send    \x05\x05\x03\x03001C000D6F0001A5A372000D6F0001A404A5CFF3\r\n
Receive \x05\x05\x03\x03000003A500C1AF55\r\n
Receive \x05\x05\x03\x03001D03A5000D6F0001A5A372000D6F0001A404A50104C2\r\n
```

Response data:

|Type|Description|Data in example|
|--|--|--|
|Uint16|Command response code|001D|
|Uint16|Sequence number|03A5|
|Uint64|Circle+ MAC|000D6F0001A5A372|
|Uint64|Removed endpoint's MAC|000D6F0001A404A5|
|Uint8|Success flag?|01|


---
###Command 0x0023 (from plugwise unleashed)
Description: Device information request

Payload data:

|Type|Description|Data in example|
|--|--|--|
|Uint64|MAC of unit to receive info from|000D6F0001A59EDC|

Example:
```
Send    \x05\x05\x03\x030023000D6F00029082EDE943\r\n
Receive \x05\x05\x03\x030000020A00C18388\r\n
Receive \x05\x05\x03\x030024020A000D6F00029082ED110B1B1A0006535801856539090011064E0844C202271C\r\n
```
When the node cannot be found the following data is received (note the ack command response code):
```
Send    \x05\x05\x03\x030023000D6F0001A404A56508\r\n
Receive \x05\x05\x03\x03000003B100C1E8B3\r\n
Receive \x05\x05\x03\x03000003B100E14215\r\n
```

When an Ack command response code is received with 0x00E1 as status the unit was not found.

Response data:

|Type|Description|Data in example|
|--|--|--|
|Uint16|Command response code|0024|
|Uint16|Sequence number|020A|
|Uint64|MAC of unit|000D6F00029082ED|
|Uint8|Internal clock year|11|
|Uint8|Internal clock month|0B|
|Uint16|Internal clock minutes|1B1A|
|Uint32|Current log address|00065358|
|Uint8|Power state.<br/>1 = on, 0 = off|01|
|Uint8|Net frequency of unit, 85 appears to be 50 Hz|85|
|String(12)|Hardware version of unit|653909001106|
|Uint32|Epoch timestamp of build date of unit|4E0844C2|
|Uint8|Trailing byte, meaning unknown|02|


Example code (credits Maarten Damen):
```python
def logaddresstoint(self, logaddress):
    """
    Converts plugwise log address to integer.
    """
    return (logaddress - 278528) / 32 

def deviceinforesponse(self, response):
    """
    Handles plugwise general device information response.
    """
    if len(response) != 70 or response.startswith(self.DEVINFORESPONSE) == False:
        print "invalid device information response"
    else:
        #print response
        macaddress  = response[8:24]
        year        = self.hextoint(response[24:26]) + 0x7d0
        month       = self.hextoint(response[26:28])
        minutes     = self.hextoint(response[28:32])

            logaddress  = self.logaddresstoint(self.hextoint(response[32:40]))
        powerstate  = self.hextoint(response[40:42])
        #herz        = self.determinehz(response[42:44])
        hwversion   = "%s-%s-%s" % (response[44:48], response[48:52], response[52:56])
        firmware     = datetime.datetime.utcfromtimestamp(self.hextoint(response[56:64])) 

        for device in self.devices:
            if device.address == macaddress:
                device = device

        status = False
        if powerstate == 1:
            status = True
        elif powerstate == 0:
            status = False


        args = [device.id, status]
        self.router.sendcommand("update_status", args, "database")
        print logaddress 
     
        # update buffer information
        if (device.lastlogaddress < logaddress):
               if device.lastlogaddress == None:
                   lastlogaddress = 0
            else:
               lastlogaddress = device.lastlogaddress

        for i in range(lastlogaddress+1, logaddress+1):
               self.get_powerbuffer(str(device.address), i)
           
           self.waitreply = False  
```

---
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


---
###Command 0x0028
Description: Unknown

Example
```
Send    \x05\x05\x03\x030028000D6F0001A5A372005614040211178BC6\r\n
Receive \x05\x05\x03\x030000017200C1601F\r\n
Receive \x05\x05\x03\x030000017200DF000D6F0001A5A372A65C\r\n
```

---
###Command 0x0029
Description: Unknown (has something to do with the Circle+)

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
|?|Unknown|57531404021117|


---
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

Response data:

|Type|Description|Data in example|
|--|--|--|
|Uint16|Command response code|003F|
|Uint16|Sequence number|00FE|
|Uint64|Endpoint MAC|000D6F0001A40223|
|?|Unknown|0E36040401457A|


---
###Command 0x0040
Description: Unknown

Example:
```
Send    \x05\x05\x03\x030040000D6F0001A402230001738B\r\n
Receive \x05\x05\x03\x03000000FF00C14CC2\r\n
Receive \x05\x05\x03\x03000000FF00E5000D6F0001A402238EE1\r\n
```

---
###Command 0x0048 (from plugwise unleashed)
Description: Read power buffer information

Payload data:

|Type|Description|Data in example|
|--|--|--|
|Uint64|Endpoint MAC|000D6F0001A40223|
|Uint16|Sequence number|00FE|
|Uint32|Log address to retrieve|00044020|

Example:
```
Send    \x05\x05\x03\x030048000D6F0001A40223000440204AAE\r\n
Receive \x05\x05\x03\x030000003700C1FD88\r\n
Receive \x05\x05\x03\x0300490037000D6F0001A40223 110B1C5C 000007C1 110B1C98 000007B8 110B1CD4 000007B7 110B1D10 000007AC000440202B72\r\n
```

Response data:

|Type|Description|Data in example|
|--|--|--|
|Uint16|Command response code|0049|
|Uint16|Sequence number|0037|
|Uint64|Endpoint MAC|000D6F0001A40223|
|Uint32|First log date|110B1C5C|
|Uint32|Total pulse count in first logged hour|000007C1|
|Uint32|Second log date|110B1C98|
|Uint32|Total pulse count in second logged hour|000007C1|
|Uint32|Third log date|110B1CD4|
|Uint32|Total pulse count in third logged hour|000007C1|
|Uint32|Fourth  log date|110B1D10|
|Uint32|Total pulse count in fourth logged hour|000007AC|
|Uint32|Log address of this buffer|00044020|

Example code (credits Maarten Damen):
```python
def clockinfotodatetime(self, year, month, minutes):
    """
    Converts plugwise device date and time information to pythonic datetime.
    """
    time = datetime.datetime(2000, 1, 1, 0, 0, 0, tzinfo=tzutc())
    if year > 2000:
        year = year - 2000

    time += relativedelta(months=+month-1, years=+year, minutes=+minutes, hours=-1)
    return time
```


---
###Command 0x004A
Description: Unknown

Example:
```
Send    \x05\x05\x03\x03004A000D6F0001A5A3723C016934\r\n
Receive \x05\x05\x03\x030000017300C1CA4E\r\n
Receive \x83'
Receive \x05\x05\x03\x030000017300F1000D6F0001A5A372AB40\r\n
```


---
###Command 0x0058
Description: Unknown

Example:
```
Send    \x05\x05\x03\x030058000D6F0001A20F97007DC0\r\n
Receive \x05\x05\x03\x030000019200C1E0BC\r\n
Receive \x05\x05\x03\x030000019200F9000D6F0001A20F97C8B3\r\n
```


---
###Command 0x005F
Description: Unknown

Example:
```
Send    \x05\x05\x03\x03005F000D6F0001A400E2FC53\r\n
Receive \x05\x05\x03\x03000000F500C1BF96\r\n
Receive \x05\x05\x03\x03006000F5000D6F0001A400E2FFFFFFFFFFFFFFFE3E91\r\n
```
