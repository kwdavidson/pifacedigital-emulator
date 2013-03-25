#!/usr/bin/env python3
import sys
import pifacedigitalio as pfio
from pifacedigitalio import OUTPUT_PORT, INPUT_PORT
from pfemgui import run_emulator
from multiprocessing import Process, Queue
from time import sleep


class EmulatorAddressError(Exception):
    pass

# replicate pifacedigitalio functions/classes
# force the classes to use the functions in this module, not the pfio
class EmulatorItem:
    @property
    def handler(self):
        return sys.modules[__name__]

class InputItem(EmulatorItem, pfio.Item):
    pass

class InputItem(EmulatorItem, pfio.InputItem):
    pass

class OutputItem(EmulatorItem, pfio.OutputItem):
    pass

class LED(EmulatorItem, pfio.LED):
    pass

class Relay(EmulatorItem, pfio.Relay):
    pass

class Switch(EmulatorItem, pfio.Switch):
    pass

class PiFaceDigital(EmulatorItem, pfio.PiFaceDigital):
    pass

class InputFunctionMap(EmulatorItem, pfio.InputFunctionMap):
    pass


def init(init_board=True):
    pfio.init(init_board)

    global proc_comms_q_to_em
    global proc_comms_q_from_em
    proc_comms_q_to_em   = Queue()
    proc_comms_q_from_em = Queue()

    # start the gui in another process
    global emulator
    emulator = Process(
            target=run_emulator,
            args=(sys.argv, proc_comms_q_to_em, proc_comms_q_from_em))
    emulator.start()

def deinit():
    # stop the gui
    global proc_comms_q_to_em
    proc_comms_q_to_em.put(('quit',))
    global emulator
    emulator.join()
    pfio.deinit()

def digital_read(pin_num, board_num=0):
    return read_bit(pin_num, pfio.INPUT_PORT, board_num) ^ 1

def digital_write(pin_num, value, board_num=0):
    write_bit(value, pin_num, pfio.OUTPUT_PORT, board_num)

def digital_read_pullup(pin_num, board_num=0):
    return read_bit(pin_num, pfio.INPUT_PULLUP, board_num)

def digital_write_pullup(pin_num, value, board_num=0):
    write_bit(value, pin_num, pfio.INPUT_PULLUP, board_num)

def get_bit_mask(bit_num):
    return pfio.get_bit_mask(bit_num)

def get_bit_num(bit_pattern):
    return pfio.get_bit_num(bit_pattern)

def read_bit(bit_num, address, board_num=0):
    global proc_comms_q_to_em
    global proc_comms_q_from_em

    if address is pfio.INPUT_PORT:
        proc_comms_q_to_em.put(('get_in', bit_num))
        return proc_comms_q_from_em.get(block=True)
    elif address is pfio.OUTPUT_PORT:
        proc_comms_q_to_em.put(('get_out', bit_num))
        return proc_comms_q_from_em.get(block=True)
    else:
        raise EmulatorAddressError(
            "Reading to 0x%X is not supported in the PiFace Digital emulator" % \
                    address)

   
def write_bit(value, bit_num, address, board_num=0):
    global proc_comms_q_to_em
    global proc_comms_q_from_em

    if address is pfio.OUTPUT_PORT:
        proc_comms_q_to_em.put(('set_out', bit_num, True if value else False))
    else:
        raise EmulatorAddressError(
            "Writing to 0x%X is not supported in the PiFace Digital emulator" % \
                    address)

def read(address, board_num=0):
    if address is pfio.INPUT_PORT or address is pfio.OUTPUT_PORT:
        value = 0x00
        for i in range(8):
            value |= read_bit(i, address, board_num) << i

        return value

    else:
        raise EmulatorAddressError(
            "Reading from 0x%X is not supported in the PiFace Digital emulator" % \
                    address)

def write(data, address, board_num=0):
    if address is pfio.OUTPUT_PORT:
        for i in range(8):
            value = (data >> i) & 1
            write_bit(value, i, address, board_num)

    else:
        raise EmulatorAddressError(
            "Writing to 0x%X is not supported in the PiFace Digital emulator" % \
                    address)


def spisend(bytes_to_send):
    raise FunctionNotImplemented("spisend")

"""
TODO have not yet implemented interupt functions in emulator
"""
def wait_for_input(input_func_map=None, loop=False, timeout=None):
    raise FunctionNotImplemented("wait_for_input")

def call_mapped_input_functions(input_func_map):
    raise FunctionNotImplemented("call_mapped_input_functions")

def clear_interupts():
    raise FunctionNotImplemented("clear_interupts")

def enable_interupts():
    raise FunctionNotImplemented("enable_interupts")

def disable_interupts():
    raise FunctionNotImplemented("disable_interupts")

if __name__ == '__main__':
    init()
