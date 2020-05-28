import logging
import pandas as pd
import matplotlib.pyplot as plt


def running_total_comparison(df1, window=15):
    fig_size = [12,12]
    xlim = [0,365]
    ylim = [0,max(df1.Pages)]
    years = df1.Year.unique()[-window:].tolist()
    y = years.pop(0)
    _df = df1.loc[df1.Year == y]
    ax = _df.plot("Day", "Pages", figsize=fig_size, xlim=xlim, ylim=ylim, label=y)
    for y in years:
        _df = df1.loc[df1.Year == y]
        ax = _df.plot("Day", "Pages", figsize=fig_size, xlim=xlim, ylim=ylim, ax=ax, label=y)


def yearly_comparisons(df, current_year=2020):
    now = df.loc[df.Year == current_year]
    fig_size = [12, 6]
    ax = df.hist("Pages Read", bins=14, color="darkblue", figsize=fig_size)
    plt.axvline(x=int(now["Pages Read"]), color="red")
    plt.show()
    df.plot.bar(x="Rank", y="Pages Read", width=.95, color="darkblue", figsize=fig_size)
    plt.axvline(x=int(now["Rank"]) - 1, color="red")
    plt.show()
    df.sort_values("Year").plot.bar(x="Year", y="Pages Read", width=.95, color="darkblue", figsize=fig_size)
    plt.show()