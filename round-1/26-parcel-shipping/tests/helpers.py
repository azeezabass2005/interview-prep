from decimal import Decimal as D

from ship.parcel import Package


def box(l, w, h, lb):
    return Package(D(str(l)), D(str(w)), D(str(h)), D(str(lb)))
