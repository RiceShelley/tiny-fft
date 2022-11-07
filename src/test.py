import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles
from scipy.fft import fft
import numpy as np
from random import randint
from cocotb.regression import TestFactory

async def do_hw_fft(dut, data_in):

    await RisingEdge(dut.clk)
    dut.wrEn.value = 1

    dut.data_in.value = int(data_in[0])
    await RisingEdge(dut.clk)
    dut.data_in.value = int(data_in[1])
    await RisingEdge(dut.clk)
    dut.data_in.value = int(data_in[2])
    await RisingEdge(dut.clk)
    dut.data_in.value = int(data_in[3])
    await RisingEdge(dut.clk)

    dut.wrEn.value = 0

    await RisingEdge(dut.clk)

    await RisingEdge(dut.rd_idx_zero)
    await RisingEdge(dut.clk)
    rtn = []
    for i in range(4):
        real = int(dut.data_out.value)
        if (real > 31):
            real -= 64
        await RisingEdge(dut.clk)
        img = int(dut.data_out.value)
        if (img > 31):
            img -= 64
        await RisingEdge(dut.clk)
        print(f"{real} + {img}j")
        rtn.append(complex(real, img))

    return rtn

async def test_hw_4bit_fft(dut, inputA, inputB, inputC, inputD):
    dut._log.info("start")
    clock = Clock(dut.clk, 10, units="us")
    cocotb.fork(clock.start())
    dut.wrEn.value = 0
    
    dut._log.info("reset")
    dut.rst.value = 1
    await ClockCycles(dut.clk, 10)
    dut.rst.value = 0
    await ClockCycles(dut.clk, 10)

    input_data = np.array([
        inputA,
        inputB,
        inputC,
        inputD])

    rslt = await do_hw_fft(dut, input_data)
    expectedRslt = fft(input_data)
    print(f"input {input_data}")
    print(f"got {rslt}")
    print(f"expected {expectedRslt}")
    for i, r in enumerate(rslt):
        assert r == expectedRslt[i]

    await Timer(20, 'us')

if cocotb.SIM_NAME:
    factory = TestFactory(test_hw_4bit_fft)
    factory.add_option("inputA", list(range(-8, 7 + 1)))
    factory.add_option("inputB", list(range(-8, 7 + 1)))
    factory.add_option("inputC", list(range(-8, 7 + 1)))
    factory.add_option("inputD", list(range(-8, 7 + 1)))
    factory.generate_tests()

