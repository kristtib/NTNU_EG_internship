import pandapower as pp

network = pp.create_empty_network(f_hz=50)
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
gen1 = pp.create_sgen(net=network, bus=bus1, p_mw=50)

trafo1 = pp.create_transformer(net=network, lv_bus=bus1, hv_bus=bus2, std_type="100 MVA 220/110 kV")


for i in range (0,3):
    pp.create_bus(
        network,
        name="bus"+str(3+i),
        vn_kv=230,
        type="b",
    ).item()

    pp.create_line(
        net=network,
        from_bus=1+i,
        to_bus=2+i,
        std_type="490-AL1/64-ST1A 110.0",
        length_km=10,
    )


pp.create_ext_grid(net=network, bus=4)
pp.runpp(net=network, algorithm="nr", run_control=True, numba=True)

pp.plotting.to_html(net=network, filename="test.html")

network.res_line.plot(y="i_ka",kind="line")

print(network)
