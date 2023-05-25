"""
This plot shows the final output of MSNoise.


.. include:: ../clickhelp/msnoise-cc-dvv-plot-dvv.rst


Example:

``msnoise cc dvv plot dvv`` will plot all defaults:

.. image:: ../.static/dvv.png

"""

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

from matplotlib.dates import DateFormatter

from ..api import *


def wavg(group, dttname, errname):
    d = group[dttname]
    group[errname][group[errname] == 0] = 1e-6
    w = 1. / group[errname]
    wavg = (d * w).sum() / w.sum()
    return wavg


def wstd(group, dttname, errname):
    d = group[dttname]
    group[errname][group[errname] == 0] = 1e-6
    w = 1. / group[errname]
    wavg = (d * w).sum() / w.sum()
    N = len(np.nonzero(w)[0])
    wstd = np.sqrt(np.sum(w * (d - wavg) ** 2) / ((N - 1) * np.sum(w) / N))
    return wstd


def get_wavgwstd(data, dttname, errname):
    grouped = data.groupby(level=0)
    g = grouped.apply(wavg, dttname=dttname, errname=errname)
    h = grouped.apply(wstd, dttname=dttname, errname=errname)
    return g, h


def main(mov_stack=None, dttname="M", components='ZZ', filterid=1,
         pairs=[], showALL=False, show=False, outfile=None):
    db = connect()
    params = get_params(db)
    start, end, datelist = build_movstack_datelist(db)

    if mov_stack != 0:
        mov_stacks = [mov_stack, ]
    else:
        mov_stacks = params.mov_stack

    if components.count(","):
        components = components.split(",")
    else:
        components = [components, ]

    low = high = 0.0
    for filterdb in get_filters(db, all=True):
        if filterid == filterdb.ref:
            low = float(filterdb.low)
            high = float(filterdb.high)
            break

    fig, axes = plt.subplots(len(mov_stacks), 1, sharex=True, figsize=(12, 9))

    plt.subplots_adjust(bottom=0.06, hspace=0.3)
    for i, mov_stack in enumerate(mov_stacks):
        current = start
        try:
            plt.sca(axes[i])
        except:
            plt.sca(axes)
        plt.title('%i Days Moving Window' % mov_stack)
        for comps in components:
            try:
                dvv = xr_get_dvv(comps, filterid, mov_stack)
            except:
                continue
            for _ in ["mean", "50%", "trimmed_mean", "weighted_mean"]:
                plt.plot(dvv.index, dvv.loc[:, ("m", _)] * -100, label="%s: %s" % (comps,_ ))
            for _ in ["5%","95%"]:
                plt.plot(dvv.index, dvv.loc[:, ("m", _)] * -100, label="%s: %s" % (comps,_ ))

        plt.ylabel('dv/v (%)')
        if i == 0:
            plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4,
                       ncol=2, borderaxespad=0.)
            left, right = dvv.index[0], dvv.index[-1]
            plt.title('1 Day')
        else:
            plt.title('%i Days Moving Window' % mov_stack)
            plt.xlim(left, right)

        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))
    fig.autofmt_xdate()
    title = '%s, Filter %d (%.2f - %.2f Hz)' % \
            (",".join(components), filterid, low, high)
    plt.suptitle(title)

    if outfile:
        if outfile.startswith("?"):
            if len(mov_stacks) == 1:
                outfile = outfile.replace('?', '%s-f%i-m%i-M%s' % (components,
                                                                   filterid,
                                                                   mov_stack,
                                                                   dttname))
            else:
                outfile = outfile.replace('?', '%s-f%i-M%s' % (components,
                                                               filterid,
                                                               dttname))
        outfile = "dvv " + outfile
        print("output to:", outfile)
        plt.savefig(outfile)
    if show:
        plt.show()


if __name__ == "__main__":
    main()
