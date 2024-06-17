import histogram as H
import h5py
import copy


def MDH2Histo(filename, Ei=None):
    """
    Load an hdf 5 file containing an MDHistogram workspace and
    populate a histogram object.
    The MDHistogram workspace must have an axis with a long_name of 'DeltaE'
    and another one with a long_name of '|Q|'.
    The units for the 'DeltaE' axis are assumed to be meV and for the '|Q|'
    axis are 1/angstrom.
    set an Attribute Ei to the histogram object.
    If Ei is None attempt to read if from the file,
    """
    datain = {}
    with h5py.File(filename) as fh:
        try:
            rh = fh["MDHistoWorkspace"]
        except KeyError:
            print("This is not an MDHistoWorkspace")
        # kys = list(rh['data'].keys())
        dh = rh["data"]
        # the following loop populates the Q and E dictionary
        # items solely on the long_name. So it works for old files
        # with data that does not match Nexus standard and new files that do.
        for idx, ky in enumerate(dh):
            atkylst = list(dh[ky].attrs.keys())
            if "long_name" in atkylst:
                if dh[ky].attrs["long_name"] == b"|Q|":
                    datain["|Q|"] = rh["data"][ky][:]
                    Qidx = copy.copy(idx)
                elif dh[ky].attrs["long_name"] == b"DeltaE":
                    datain["DeltaE"] = dh[ky][:]
                    Eidx = copy.copy(idx)
                else:
                    datain[ky] = dh[ky][:]
            else:
                datain[ky] = dh[ky][:]

        if Ei is None:
            try:
                Ei = rh["experiment0/logs/Ei"]["value"][:][0]
            except:
                print("Problem reading Ei from{}".format(filename))
    data = datain["signal"] / datain["num_events"]
    err2 = datain["errors_squared"] / (datain["num_events"] ** 2)
    # transpose data if it is from a file with Energy axis before the Q axis.
    # print("Qidx={}, Eidx={}".format(Qidx, Eidx))
    data = data.T
    err2 = err2.T
    qaxis = H.axis("Q", boundaries=datain["|Q|"], unit="1./angstrom")
    eaxis = H.axis("E", boundaries=datain["DeltaE"], unit="meV")
    hist = H.histogram("IQE", (qaxis, eaxis), data=data, errors=err2)
    hist.setAttribute("Ei", Ei)
    return hist
