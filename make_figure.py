import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

mpl.rc("font", family="Arial")

faostat_country_groups = pd.read_csv("FAOSTAT_data_2-9-2021.csv")[
    ["Country Group", "ISO3 Code"]
].dropna()

included_groups = [
    "Asia",
    "Europe",
    "Latin America and the Caribbean",
    "Northern America",
    "Africa",
    "Australia and New Zealand",
]

group_by_iso3 = faostat_country_groups.loc[
    lambda d: d["Country Group"].isin(included_groups)
].set_index("ISO3 Code")["Country Group"]

oecd_balances = (
    pd.read_csv(
        "AEI_NUTRIENTS_09022021110826440.csv",
        index_col=[
            "COUNTRY",
            "Indicator",
            "NUTRIENTS",
            "Unit Code",
            "TIME",
        ],
    )
    .xs("Balance per hectare", level="Indicator")
    .xs("NITROGEN", level="NUTRIENTS")
    .xs("KG", level="Unit Code")
    .drop(2018, level="TIME") # drop year 2018 due to limited data coverage
    .join(group_by_iso3, on="COUNTRY")
    .reset_index()
    .set_index(["Country Group", "COUNTRY", "TIME"])
    .Value
)

print(oecd_balances)


colors = mpl.cm.tab10.colors

group_order = (
    oecd_balances.xs(2017, level="TIME")
    .groupby("Country Group")
    .mean()
    .sort_values(ascending=False)
    .index
)

fig, ax = plt.subplots(1, 1, figsize=(4, 5))
for group, color in zip(group_order, colors):
    d = oecd_balances.xs(group).unstack("COUNTRY")
    band_width = 2 * d.std(axis=1)
    mean = d.mean(axis=1)
    ax.fill_between(
        d.index,
        mean + band_width / 2,
        mean - band_width / 2,
        color=(*color, 0.1),
    )
    ax.plot(
        d.mean(axis=1),
        lw=3,
        color=color,
        label=f"{group} (n={len(d.columns)})",
    )
ax.grid(True)
ax.set_title("Gross N balances (group means ± 1 stdev)")
ax.set_ylabel("kg N/ha agricultural area")
ax.set_xlabel("Year")
ax.legend(bbox_to_anchor=(0, -0.2), loc="upper left", frameon=False)
ax.set_ylim(-20, 150)
fig.set_tight_layout(True)
fig.savefig("oecdstat-gnb-regions.pdf")
fig.savefig("oecdstat-gnb-regions.png", dpi=300)
