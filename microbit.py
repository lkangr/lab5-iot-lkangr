cmd = ""
state = 0
count = 0

def on_data_received():
    global cmd, state
    cmd = serial.read_until(serial.delimiters(Delimiters.HASH))
    # basic.show_string(cmd)
    if cmd == "0":
        basic.show_icon(IconNames.SAD)
    elif cmd == "1":
        basic.show_icon(IconNames.HAPPY)
    elif cmd == "2":
        basic.show_icon(IconNames.SMALL_HEART)
    elif cmd == "3":
        basic.show_icon(IconNames.HEART)
    elif cmd == "4":
        state = 1
    if cmd != "4":
        serial.write_string("!1:ACK:1#")
serial.on_data_received(serial.delimiters(Delimiters.HASH), on_data_received)

def on_forever():
    global count, state
    if state == 0:
        count = 10
        state = 1
    elif state == 1:
        if count == 10:
            serial.write_string("!1:TEMP:" + ("" + str(input.temperature())) + "#")
            state = 2
        elif count == 5:
            serial.write_string("!1:LIGHT:" + ("" + str(input.light_level())) + "#")
            state = 2
    elif state == 2:
        pass
    count += -1
    if count == 0:
        count = 10
    basic.pause(1000)
basic.forever(on_forever)
