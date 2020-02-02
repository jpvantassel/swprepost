"""This file defines the `Suite` class."""

class Suite():

    def __init__():
        pass
    
    def misfit_range(self, nmodels="all"):
        """Return range of misfits for nmodels.
        
        Args:
            nmodels : {int, "all"}, optional
                Number of models to consider, default is 'all' so all
                avaiable models will be considered.

        Returns:
            If nmodels==1:
                `float` corresponding to the single best misfit.
            else:
                Tuple of the form (min_msft, max_msft).
        """
        if nmodels == "all":
            return (self.misfits[0], self.misfits[-1])
        elif nmodels == 1:
            return self.misfits[0]
        else:
            return (self.misfits[0], self.misfits[nmodels-1])

    def misfit_repr(self, nmodels="all"):
        """Return string representation of misfit [min-max] or [min]."""
        if nmodels==1:
            return f"[{round(self.misfits[0],2)}]"
        else:
            min_msft, max_msft = self.misfit_range(nmodels=nmodels)
            return f"[{round(min_msft,2)}-{round(max_msft,2)}]"
