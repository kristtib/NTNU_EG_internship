import pandapower as pp
import numpy as np
import matplotlib.pyplot as plt
from cable_options import add_cables_to_std_library
from trafo_options import add_trafos_to_std_library


def calulate_q_statcom(sgen_p= float, sgen_q = float):
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
        name="mv_bus",
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
    gen=pp.create_sgen(net=network, bus=bus_mv, p_mw=sgen_p,q_mvar=sgen_q)
    
    trafo1=pp.create_transformer3w(net=network, hv_bus=bus_hv, mv_bus=bus_mv, lv_bus=bus_lv, std_type="on_tx_400kV_220kV_36kV_450MVA")
    #trafo_tap = pp.create_transformer(net=network, lv_bus = bus_lv, hv_bus = bus_hv, std_type="ONS_tx_400kV_230kV_400MVA")
    
    grid=pp.create_ext_grid(net=network, bus=bus_hv)
    statcom=pp.create_load(net=network,bus=bus_lv,const_i_percent=100,q_mvar=0,p_mw=0)

    pp.runpp(net=network, algorithm="nr", run_control=True, numba=True,tolerance_mva=1e-6)
    pp.plotting.to_html(net=network, filename="test.html")

    plt.figure()
    plt.xlabel('Q_sys [MVAr]')
    plt.ylabel('P_in [MW]')
    
    active_powers=[]
    reactive_power_no_statcom=[]
    step_p = int(sgen_p/10)
    for i in range (0,sgen_p+step_p,step_p):
            network.sgen.p_mw.iloc[0]=i 
            pp.runpp(net=network, algorithm="nr", run_control=True, numba=True,tolerance_mva=1e-6)       
            active_powers.append(i)
            reactive_power_no_statcom.append(network.res_bus.iloc[bus_hv].q_mvar)

    #for q in [-150,150]:
        #network.load.q_mvar.iloc[0]=q

    reactive_powers_min=[]
    reactive_powers_max=[]
    reactive_power_statcom=[]

    network.load.q_mvar.iloc[0]=-150
    for i in range (0,sgen_p+step_p,step_p):
        network.sgen.p_mw.iloc[0]=i 
        pp.runpp(net=network, algorithm="nr", run_control=True, numba=True,tolerance_mva=1e-6)       
        reactive_powers_min.append(network.res_bus.iloc[bus_hv].q_mvar)
        
    network.load.q_mvar.iloc[0]=150
    for i in range (0,sgen_p+step_p,step_p):
        network.sgen.p_mw.iloc[0]=i 
        pp.runpp(net=network, algorithm="nr", run_control=True, numba=True,tolerance_mva=1e-6)       
        reactive_powers_max.append(network.res_bus.iloc[bus_hv].q_mvar)
        
    array1=np.array(reactive_power_no_statcom)
    array2=np.array(reactive_powers_min)
    array3=np.array(reactive_powers_max)

    reactive_power_statcom_min=array2-array1
    reactive_power_statcom_max=array3-array1
    plt.plot(reactive_power_statcom_min, active_powers)
    plt.plot(reactive_power_statcom_max, active_powers)
    
    #plt.fill_between(reactive_power_statcom_min, 0, active_powers, where=(reactive_power_statcom_min >= reactive_power_statcom_max[0]) & (reactive_power_statcom_min <= reactive_power_statcom_max[1]), color='yellow', alpha=0.3)

    plt.legend(loc="lower left")
    plt.grid()
    plt.show()

    return network

network=calulate_q_statcom(400,0)
print('hei')