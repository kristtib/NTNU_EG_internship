import pandapower as pp


def add_cable_to_pp_net_library(net, cable):
    try:
        value = {
            "r_ohm_per_km": cable["r_ohm_per_km"],
            "x_ohm_per_km": cable["x_ohm_per_km"],
            "c_nf_per_km": cable["c_nf_per_km"],
            "max_i_ka": cable["max_i_ka"],
            "type": "cs",
            "q_mm2": cable["q_mm2"],
        }

        pp.create_std_type(
            net,
            name=cable["name"],
            data=value,
            element="line",
        )
    except Exception:
        return


def add_cables_to_std_library(net):
    cables = [
        {
            "name": "245kv_1000mm2_cu",
            "r_ohm_per_km": 0.027458539530619,
            "x_ohm_per_km": 0.119380520836412,
            "c_nf_per_km": 190,
            "max_i_ka": 0.9672101038734946,
            "q_mm2": 1000,
        },
        {
            "name": "245kv_1200mm2_cu",
            "r_ohm_per_km": 0.021337578768921,
            "x_ohm_per_km": 0.114969724750772,
            "c_nf_per_km": 204.04,
            "max_i_ka": 1.0224576113299597,
            "q_mm2": 1200,
        },
        {
            "name": "245kv_1200mm2_al",
            "r_ohm_per_km": 0.029548550501489,
            "x_ohm_per_km": 0.116644193635135,
            "c_nf_per_km": 198.71,
            "max_i_ka": 0.8984247966775813,
            "q_mm2": 1200,
        },
    ]
    for cable in cables:
        add_cable_to_pp_net_library(net, cable)
