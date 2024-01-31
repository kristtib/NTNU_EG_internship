import pandapower as pp
import numpy as np
import matplotlib.pyplot as plt
from cable_options import add_cables_to_std_library
from trafo_options import add_trafos_to_std_library

def generate_basic_network():
    network = pp.create_empty_network(f_hz=50)
    add_cables_to_std_library(network)
    add_trafos_to_std_library(network)

    pp.create_bus(
        network,
        name="bus1",
        vn_kv=66,
        type="b",
    ).item()
    pp.create_bus(
        network,
        name="bus2",
        vn_kv=230,
        type="b",
    ).item()

    pp.create_sgen(net=network, bus=0, p_mw=400,q_mvar=-75)
    pp.create_transformer(
        net=network, lv_bus=0, hv_bus=1, std_type="OFS_tx_220kV_66kV_400MVA"
    )

    total_line_length = 80 #km
    per_line_length = 1
    for i in range(0, total_line_length, per_line_length):
        pp.create_bus(
            network,
            name="bus"+str(network.bus.iloc[-1].name+2),
            vn_kv=230,
            type="b",
        ).item()

        pp.create_line(
            net=network,
            name=f"line{i+per_line_length}",
            from_bus=network.bus.iloc[-2].name,
            to_bus=network.bus.iloc[-1].name,
            std_type="245kv_1000mm2_cu",
            # std_type="490-AL1/64-ST1A 110.0",
            length_km=per_line_length,
        )
    
    pp.create_bus(
            network,
            name="bus"+str(network.bus.iloc[-1].name+2),
            vn_kv=400,
            type="b",
        ).item()
    pp.create_transformer(
        net=network, lv_bus=network.bus.iloc[-2].name, hv_bus=network.bus.iloc[-1].name, std_type="ONS_tx_400kV_230kV_400MVA"
    )

    pp.create_ext_grid(net=network, bus=network.bus.iloc[-1].name)
    pp.runpp(net=network, algorithm="nr", run_control=True, numba=True)
    pp.plotting.to_html(net=network, filename="test.html")

    return network

def line_current_plot(network):
    line_names = network.line["name"]
    line_currents = network.res_line["i_ka"]
    plt.plot(line_names, line_currents)
    plt.show()
     

n = generate_basic_network()
line_current_plot(n)
