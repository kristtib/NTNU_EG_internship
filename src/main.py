import pandapower as pp
import matplotlib.pyplot as plt

from cable_options import add_cables_to_std_library

network = pp.create_empty_network(f_hz=50)
add_cables_to_std_library(network)
bus1 = pp.create_bus(
    network,
    name="bus1",
    vn_kv=100,
    type="b",
).item()
bus2 = pp.create_bus(
    network,
    name="bus2",
    vn_kv=230,
    type="b",
).item()
gen1 = pp.create_sgen(net=network, bus=bus1, p_mw=300)

trafo1 = pp.create_transformer(
    net=network, lv_bus=bus1, hv_bus=bus2, std_type="100 MVA 220/110 kV"
)


for i in range(0, 8):
    pp.create_bus(
        network,
        name="bus" + str(3 + i),
        vn_kv=230,
        type="b",
    ).item()

    pp.create_line(
        net=network,
        name=f"line{i}",
        from_bus=1 + i,
        to_bus=2 + i,
        std_type="245kv_1000mm2_cu",
        length_km=10,
    )


pp.create_ext_grid(net=network, bus=9)
pp.runpp(net=network, algorithm="nr", run_control=True, numba=True)

pp.plotting.to_html(net=network, filename="test.html")


line_names = network.line["name"]
loading_percentages = network.res_line["loading_percent"]
plt.plot(line_names, loading_percentages)
plt.show()
print(network)
