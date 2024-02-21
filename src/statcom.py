import pandapower as pp
import numpy as np
import matplotlib.pyplot as plt
from cable_options import add_cables_to_std_library
from trafo_options import add_trafos_to_std_library


def generate_basic_network(sgen_p= float, sgen_q = float):
    network = pp.create_empty_network(f_hz=50)
    
    on_tx_400kV_220kV_36kV_450MVA = { "name": "on_tx_400kV_220kV_36kV_450MVA", "sn_hv_mva": 450, "sn_mv_mva": 380, "sn_lv_mva": 250, "vn_hv_kv": 410, "vn_mv_kv": 230, "vn_lv_kv": 35.7, "vk_hv_percent": 13,
                                     "vk_mv_percent": 15, "vk_lv_percent": 18, "vkr_hv_percent": 0.17, "vkr_mv_percent": 0.35, "vkr_lv_percent": 0.44, "pfe_kw": 114 ,
                                     "i0_percent": 0.2, "shift_mv_degree": 0, "shift_lv_degree": 0, "vector_group": "YNyn0d11", "tap_side": "hv",   "tap_neutral": 0,
                                     "tap_min": -10,    "tap_max": 10,  "tap_step_percent": 1.5 }

    pp.create_std_type(
            network,
            name=on_tx_400kV_220kV_36kV_450MVA["name"],
            data=on_tx_400kV_220kV_36kV_450MVA,
            element="trafo3w",
        )
    
    add_trafos_to_std_library(network)
    bus_mv = pp.create_bus(
        network,
        name="lv_bus",
        vn_kv=230,
        type="b",
    ).item()
    bus_hv = pp.create_bus(
        network,
        name="hv_bus",
        vn_kv=400,
        type="b",
    ).item()
    bus_lv=pp.create_bus(
        network,
        name="lv_bus",
        vn_kv=35.7,
        type="b"
    ).item()
    pp.create_sgen(net=network, bus=bus_mv, p_mw=sgen_p,q_mvar=sgen_q)
    
    trafo1=pp.create_transformer3w(net=network, hv_bus=bus_hv, mv_bus=bus_mv, lv_bus=bus_lv, std_type="on_tx_400kV_220kV_36kV_450MVA")
    #trafo_tap = pp.create_transformer(net=network, lv_bus = bus_lv, hv_bus = bus_hv, std_type="ONS_tx_400kV_230kV_400MVA")
    
    pp.create_ext_grid(net=network, bus=network.bus.iloc[-1].name)
    pp.create_sgen(net=network, bus=bus_mv, p_mw=0, current_source=True)

    pp.runpp(net=network, algorithm="nr", run_control=True, numba=True)
    pp.plotting.to_html(net=network, filename="test.html")

    return network

network=generate_basic_network(400,0)