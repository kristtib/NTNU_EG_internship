import pandapower as pp
import numpy as np
import matplotlib.pyplot as plt
from cable_options import add_cables_to_std_library
from trafo_options import add_trafos_to_std_library
import pandapower.control as ct

def simplified_Q_trafo (P_mw, Q_mvar, k, S_base_mva):
    P_pu = P_mw/S_base_mva
    #S_pu = np.sqrt(P_mw**2 + Q_mvar**2)/S_base_mva 
    Q_simplified_trafo = -1*((k * P_pu**2)*S_base_mva)
    return Q_simplified_trafo

def generate_basic_network(sgen_p= float, sgen_q = float):
    network = pp.create_empty_network(f_hz=50)
    
    add_trafos_to_std_library(network)

    bus_lv = pp.create_bus(
        network,
        name="bus1",
        vn_kv=230,
        type="b",
    ).item()
    bus_hv = pp.create_bus(
        network,
        name="bus2",
        vn_kv=400,
        type="b",
    ).item()


    pp.create_sgen(net=network, bus=bus_lv, p_mw=sgen_p,q_mvar=sgen_q)

    
    trafo_tap = pp.create_transformer(net=network, lv_bus = bus_lv, hv_bus = bus_hv, name = " trafo_tap ",std_type="ONS_tx_400kV_230kV_400MVA", tap_pos = 0) #APPLY TAP CHANGER 
    pp.create_ext_grid(net=network, bus=network.bus.iloc[-1].name)

    ct.ContinuousTapControl(network,tid = trafo_tap, vm_set_pu=1 ,side ='lv') #discrete tap controller

    pp.runpp(net=network, algorithm="nr", run_control=True, numba=True)
    pp.plotting.to_html(net=network, filename="tap_changer.html")

    return network

def p_q_plot_tap(sgen_p=float, sgen_q=float , Vgrid=list):
    
    fig, (ax1, ax2, ax3) = plt.subplots(3,1, figsize=(10, 8))
    ax1.set_xlabel('Q_trafo [MVAr]')
    ax1.set_ylabel('P_in [MW]')
    ax2.set_xlabel('P_in [MW]')    
    ax2.set_ylabel('Difference Q (simplified - Load Flow) [MVAr]')
    ax3.set_ylabel('Difference HV and LV')
    ax3.set_xlabel('P_in [MW]')

    network = generate_basic_network(sgen_p, sgen_q=0)

    k = network.trafo.vk_percent / 100
    S_base = network.trafo.sn_mva
    simplified_Q = []
    step_p = int(sgen_p / 10)
    for i in range(0, sgen_p + step_p, step_p):
        simplified_Q.append(simplified_Q_trafo(i, sgen_q, k, S_base))

    ax1.plot(simplified_Q, range(0, sgen_p + step_p, step_p), label=f"Q_trafo simplified [MVAr]", color ='black', linewidth ='3')
    
    for v in Vgrid:
        network.ext_grid.vm_pu.iloc[0] = v/100
        active_powers = []
        reactive_powers = []   
        delta_Q = [] 
        delta_V = [] # Initialize delta for each sgen_q
        step_p = int(sgen_p / 10)
        
        for i in range(0, sgen_p + step_p, step_p):
            network.sgen.p_mw.iloc[0] = i
            pp.runpp(net=network, algorithm="nr", run_control=True, numba=True)
            active_powers.append(i)
            reactive_powers.append(network.res_bus.iloc[-1].q_mvar - sgen_q)
            difference_Q = simplified_Q_trafo(i, sgen_q, k, S_base) - (network.res_bus.iloc[-1].q_mvar - sgen_q)
            delta_Q.append(difference_Q)
            difference_V = network.res_bus.iloc[0].vm_pu - network.res_bus.iloc[-1].vm_pu
            delta_V.append(difference_V)
        
        ax1.plot(reactive_powers, active_powers, label=f"Q_trafo with load flow analysis, V_grid ={v/100}[pu]")
        ax2.plot(active_powers,delta_Q, label=f"Difference (simplified - Load Flow) Q_trafo, V_grid ={v/100}[pu]")
        ax3.plot(active_powers, delta_V, label=f"Voltage difference between V_grid and LV side, V_grid={v/100}[pu]")

    ax2.set_ylim(0,1)
    ax1.legend(loc="lower left")
    ax1.grid()
    ax2.legend(loc="upper left")
    ax2.grid()
    ax3.legend(loc="upper left")
    ax3.grid()
    plt.tight_layout()
    plt.show()

Vgrid_range = range(90,111,5)

p_q_plot_tap(400,0, Vgrid_range)

