
"""
Usage:
    ahcplot.py <ahc_dat> <axis> [-r]

Options:
    <ahc_dat>           wtで計算したahcのfile
    <axis>              x,y,z
    -r                  ahcの値の正負を反転する
"""

from docopt import docopt
from matplotlib import pyplot as plt
import plottool as pt

pt.mpl_init()

def read_ahc_dat(file_ahc_dat, ahcrow, rv):
    with open(file_ahc_dat, 'r') as f_ahc_dat:
        lines = [ l.split() for l in f_ahc_dat.readlines()[3:] ]
    Ene = [ float(line[0]) for line in lines ]
    if rv : AHC = [ -float(line[ahcrow]) for line in lines ]
    else  : AHC = [ float(line[ahcrow]) for line in lines ]
    return Ene, AHC

def main():
    args = docopt(__doc__)
    ahcrow = { 'x':2, 'y':3, 'z':1 }
    Ene, AHC = read_ahc_dat(args['<ahc_dat>'], ahcrow[args['<axis>']], args['-r'])
    fig, ax = pt.MakeAxesTable([1], [1], width=16, height=16, margin=2.5)
    pt.AHCplot(ax[0][0], Ene, AHC)
    ax[0][0].tick_params('x', labelsize=15)
    ax[0][0].tick_params('y', labelsize=15)
    ax[0][0].xaxis.label.set_size(20)
    ax[0][0].yaxis.label.set_size(20)
    plt.show()

if __name__ == '__main__': main()


