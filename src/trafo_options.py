import pandapower as pp

def add_trafo_to_pp_net_library(net, trafo):
    try:
        value = {
            "sn_mva":trafo["sn_mva"], 
                                "vn_hv_kv":trafo["vn_hv_kv"] , 
                                "vn_lv_kv":trafo["vn_lv_kv"], 
                                "vk_percent": trafo["vk_percent"], 
                                "vkr_percent": trafo["vkr_percent"], 
                                "pfe_kw": trafo["pfe_kw"], 
                                "i0_percent": trafo["i0_percent"] , 
                                "shift_degree": trafo["shift_degree"],
                                "vector_group": trafo["vector_group"], 
                                "tap_side": trafo["tap_side"],   
                                "tap_neutral": trafo["tap_neutral"],                                    
                                "tap_min": trafo["tap_min"],  
                                "tap_max": trafo["tap_max"],    
                                "tap_step_percent": trafo["tap_step_percent"]
        }

        pp.create_std_type(
            net,
            name=trafo["name"],
            data=value,
            element="trafo",
        )

    except Exception:
        return


def add_trafos_to_std_library(net):
    trafos = [
                            {"name": "OFS_tx_220kV_66kV_400MVA",
                             "sn_mva": 400, 
                                "vn_hv_kv": 230 , 
                                "vn_lv_kv": 66, 
                                "vk_percent": 12, 
                                "vkr_percent": 0.23, 
                                "pfe_kw": 117, 
                                "i0_percent": 0.06 , 
                                "shift_degree": 0,
                                "vector_group": "YNd11", 
                                "tap_side": "hv",   
                                "tap_neutral": 0,                                    
                                "tap_min": -5,  
                                "tap_max": 5,    
                                "tap_step_percent": 1.25},
                                        

                            {"name": "ONS_tx_400kV_230kV_400MVA",
                             "sn_mva": 400, 
                                "vn_hv_kv": 400 , 
                                "vn_lv_kv": 230, 
                                "vk_percent": 12, 
                                "vkr_percent": 0.23, 
                                "pfe_kw": 117, 
                                "i0_percent": 0.06 , 
                                "shift_degree": 0,                                     
                                "vector_group": "YNd11",    
                                "tap_side": "hv",   
                                "tap_neutral": 0,                                    
                                "tap_min": -10, "tap_max": 10,  "tap_step_percent": 1.25},

                            {"name" : "on_tx_400kV_220kV_36kV_450MVA", 
                             "sn_hv_mva": 450, 
                             "sn_mv_mva": 380, 
                             "sn_lv_mva": 250, 
                             "vn_hv_kv": 410, 
                             "vn_mv_kv": 230, 
                             "vn_lv_kv": 35.7, 
                             "vk_hv_percent": 13,
                                     "vk_mv_percent": 15, 
                                     "vk_lv_percent": 18, 
                                     "vkr_hv_percent": 0.17, 
                                     "vkr_mv_percent": 0.35, 
                                     "vkr_lv_percent": 0.44, 
                                     "pfe_kw": 114 ,
                                     "i0_percent": 0.2, 
                                     "shift_mv_degree": 0, 
                                     "shift_lv_degree": 0, 
                                     "vector_group": "YNyn0d11", 
                                     "tap_side": "hv",   
                                     "tap_neutral": 0,
                                     "tap_min": -10,    
                                     "tap_max": 10,  
                                     "tap_step_percent": 1.5 }    
                ]
    for trafo in trafos:
        add_trafo_to_pp_net_library(net, trafo)

