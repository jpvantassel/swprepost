

class Suite():

    def __init__():
        pass
    
    def misfit_range(self, nmodels=None):
        """Return a with the minimum and maximum misfit for nprofile."""
        if nmodels == None:
            return (self.misfits[0], self.misfits[-1])
        else:
            return (self.misfits[0], self.misfits[nmodels-1])

    def misfit_repr(self, nmodels=None):
        """Return string representation of misfit [min-max] or [min]."""

        if nmodels==1:
            return f"[{round(self.misfits[0],2)}]"
        else:
            min_msft, max_msft = self.misfit_range(nmodels=nmodels)
            return f"[{round(min_msft,2)}-{round(max_msft,2)}]"
        


    # TODO (jpv): Allow "all".
    # TODO (jpv): Comment character in from_csv.
    # TODO (jpv): From suites is very slow. Might be sort issue?

