import pandas as pd
import matplotlib.pyplot as plt


def running_total_comparison(df1, window=15):
    df1 = df1.set_index("ReadDate")
    df1.index = pd.to_datetime(df1.index)
    df1 = df1.groupby(df1.index.to_period('y')).cumsum().reset_index()
    df1["Day"] = df1.ReadDate.apply(lambda x: x.dayofyear)
    df1["Year"] = df1.ReadDate.apply(lambda x: x.year)
    fig_size = [12, 12]
    xlim = [0, 365]
    ylim = [0, max(df1.Pages)]
    years = df1.Year.unique()[-window:].tolist()
    y = years.pop(0)
    this_year = max(years)
    _df = df1.loc[df1.Year == y]
    ax = _df.plot("Day", "Pages", figsize=fig_size, xlim=xlim, ylim=ylim, label=y)
    for y in years:
        _df = df1.loc[df1.Year == y]
        lw = 3 if y == this_year else 1
        ax = _df.plot("Day", "Pages", figsize=fig_size, xlim=xlim, ylim=ylim, ax=ax, label=y, lw=lw)
    plt.show()


def yearly_comparisons(df, current_year=2020):
    now = df.loc[df.year == current_year]
    fig_size = [12, 6]
    ax = df.hist("pages read", bins=14, color="darkblue", figsize=fig_size)
    plt.axvline(x=int(now["pages read"]), color="red")
    plt.show()
    df.plot.bar(x="rank", y="pages read", width=.95, color="darkblue", figsize=fig_size)
    plt.axvline(x=int(now["rank"]) - 1, color="red")
    plt.show()
    df.sort_values("year").plot.bar(x="year", y="pages read", width=.95, color="darkblue", figsize=fig_size)
    plt.show()
