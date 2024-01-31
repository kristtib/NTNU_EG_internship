import pandapower as pp
import numpy as np
import matplotlib.pyplot as plt
from cable_options import add_cables_to_std_library
from trafo_options import add_trafos_to_std_library

def generate_basic_network(sgen_p= float, sgen_q = float, total_line_length = float, per_line_length = float):
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

    pp.create_sgen(net=network, bus=0, p_mw=sgen_p,q_mvar=sgen_q)
    pp.create_transformer(
        net=network, lv_bus=0, hv_bus=1, std_type="OFS_tx_220kV_66kV_400MVA"
    )

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

def line_current_plot(sgen_p= float, sgen_q = list, total_line_length = float, per_line_length = float):
    plt.figure()
    plt.xlabel('line length [km]')
    plt.ylabel('I [kA]')
    for q in sgen_q:
        network = generate_basic_network(sgen_p=sgen_p, sgen_q=q, total_line_length=total_line_length, per_line_length=per_line_length)
        
        line_names = network.line["name"]
        line_currents = network.res_line["i_ka"]
        
        plt.plot(line_names, line_currents, label=f"Q={q}[MVAr]")
    plt.legend(loc="upper right")
    plt.grid()
    
    
     
def p_q_plot(sgen_p= float, sgen_q = list, total_line_length = float, per_line_length = float):
    plt.figure()
    plt.xlabel('Q_sys [MVAr]')
    plt.ylabel('P [MW]')

    for q in sgen_q:
        active_powers = []
        reactive_powers = []
        step_p = int(sgen_p/10)
        for i in range (0,sgen_p+step_p,step_p):
            network = generate_basic_network(sgen_p=i, sgen_q=q, total_line_length=total_line_length, per_line_length=per_line_length)
            active_powers.append(i)
            reactive_powers.append(network.res_bus.iloc[-1].q_mvar - q)

        plt.plot(reactive_powers, active_powers, label=f"Q={q}[MVAr]")
    
    plt.legend(loc="upper right")
    plt.grid()
    plt.show()

list_of_q = range(-100,-50,10)
line_current_plot(400,list_of_q,80,1)
p_q_plot(400,list_of_q,80,1)
#n = generate_basic_network()
