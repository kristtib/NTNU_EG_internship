import pandapower as pp
import numpy as np
from cable_options import add_cables_to_std_library

def generate_basic_network():
    network = pp.create_empty_network(f_hz=50)
    add_cables_to_std_library(network)
    bus1 = pp.create_bus(
        network,
        name="bus1",
        vn_kv=66,
        type="b",
    ).item()
    bus2 = pp.create_bus(
        network,
        name="bus2",
        vn_kv=230,
        type="b",
    ).item()

    gen1 = pp.create_sgen(net=network, bus=bus1, p_mw=300,q_mvar=0)
    trafo1 = pp.create_transformer(
        net=network, lv_bus=bus1, hv_bus=bus2, std_type="100 MVA 220/110 kV"
    )

    for i in range(0, 10):
        pp.create_bus(
            network,
            name="bus" + str(network.bus.iloc[-1].name + 1),
            vn_kv=230,
            type="b",
        ).item()

        pp.create_line(
            net=network,
            name=f"line{i}",
            from_bus=network.bus.iloc[-2].name,
            to_bus=network.bus.iloc[-1].name,
            std_type="245kv_1000mm2_cu",
            # std_type="490-AL1/64-ST1A 110.0",
            length_km=10,
        )
    
    pp.create_bus(
            network,
            name="bus" + str(network.bus.iloc[-1].name + 1),
            vn_kv=400,
            type="b",
        ).item()

    trafo2 = pp.create_transformer(
        net=network, lv_bus=network.bus.iloc[-2].name, hv_bus=network.bus.iloc[-1].name, std_type="160 MVA 380/110 kV"
    )

    pp.create_ext_grid(net=network, bus=network.bus.iloc[-1].name)
    pp.runpp(net=network, algorithm="nr", run_control=True, numba=True)

    return network

